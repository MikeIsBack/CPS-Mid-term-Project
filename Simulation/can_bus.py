class CANBus:
    def __init__(self):
        self.current_transmissions = []  # Tracks ongoing transmissions on the bus
        # this array is used to detect whenever we have more than 1 msg

    def send_frame(self, frame, ecu):
        """Place a frame on the CAN bus."""
        self.current_transmissions.append((frame, ecu))  # Add frame to the queue


    def handle_arbitration(self):
        error_found = False
        winner_frame, winner_ecu = self.current_transmissions[0]

        for frame, ecu in self.current_transmissions:
            # Check if IDs are identical, then compare DLC
            if frame['id'] == winner_frame['id']:
                # Compare DLC (dominant bit wins)
                for bit_a, bit_b in zip(frame['dlc'], winner_frame['dlc']):
                    if bit_a != bit_b:
                        if bit_a == '0' and bit_b == '1':
                            error_found = True
                            winner_frame, winner_ecu = frame, ecu #switch to atker winner frame and ecu
                        break
        
        return winner_frame, winner_ecu, error_found


    def resolve_collisions(self):
        active_error_flag = {'id': "000000"}
        passive_error_flag = {'id': "111111"}

        if len(self.current_transmissions) > 1: #the collission is identified whenever we have >1 frame on the can bus
            print(f"[CANBus] Collision detected among {len(self.current_transmissions)} nodes.")

            self.current_transmissions.sort(key=lambda x: x[0]['id']) 
            #lower IDs goes first in the array of current transmission in the bus, so the winner frame will be the first one in the array
            winner_frame, winner_ecu = self.current_transmissions[0] #will take the victim
            
            real_winner_frame, real_winner_ecu, error_found = self.handle_arbitration() #understand if there's an error
            if(error_found and not winner_ecu.is_error_passive): 
                self.current_transmissions.append((active_error_flag, winner_ecu)) #store who sent the error in the bus 
                winner_ecu.increment_error_counter(is_transmit_error=True)

            if any(transmission[0] == active_error_flag for transmission in self.current_transmissions):
                real_winner_ecu.increment_error_counter(is_transmit_error=True)


            while any(flag[0] == active_error_flag for flag in self.current_transmissions): #retransmission
                self.current_transmissions = [t for t in self.current_transmissions if t[0] != active_error_flag]
                real_winner_frame, real_winner_ecu, error_found = self.handle_arbitration()

                if(error_found): 
                    if(winner_ecu.is_error_passive):
                        self.current_transmissions.append((passive_error_flag,winner_ecu)) #now victim ecu is in error passive mode
                        print(f"[{winner_ecu.name}] In Error-Passive: Transmitting Passive Error Flag (111111).")
                    else:
                        self.current_transmissions.append((active_error_flag, winner_ecu)) #store who sent the error in the bus 
                        print(f"[{winner_ecu.name}] In Error-Active: Transmitting Active Error Flag (000000).")
                        winner_ecu.increment_error_counter(is_transmit_error=True)  

                if any(transmission[0] == active_error_flag for transmission in self.current_transmissions):
                    real_winner_ecu.increment_error_counter(is_transmit_error=True)

            winner_ecu.increment_error_counter(is_transmit_error=True) # victim increases its TEC due to failed passive error flag tx

            self.current_transmissions = [t for t in self.current_transmissions if t != (real_winner_frame, real_winner_ecu)]
            print(f"[CANBus] Frame successfully transmitted: {real_winner_frame['id']} by {real_winner_ecu.name}")
            real_winner_ecu.decrement_error_counters() # due to successful tx, attacker decreases its TEC
            self.current_transmissions.clear() # victim successfully delivers its pending transmissions
            winner_ecu.decrement_error_counters() # due to successful tx, victim decreases its TEC

        elif self.current_transmissions:
            frame, sender = self.current_transmissions.pop(0)
            print(f"[CANBus] Frame successfully transmitted: {frame['id']} by {sender.name}")
            sender.decrement_error_counters()
            return frame
        
    def receive_frame(self):
        """Retrieve and process the next frame."""
        if not self.current_transmissions:  # Check if there are frames to process
            return None
        return self.resolve_collisions()  # Resolve any collisions
