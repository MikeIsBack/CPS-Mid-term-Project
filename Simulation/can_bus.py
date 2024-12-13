class CANBus:
    def __init__(self):
        self.current_transmissions = []  # Tracks ongoing transmissions on the bus

    def send_frame(self, frame, ecu):
        """Place a frame on the CAN bus."""
        self.current_transmissions.append((frame, ecu))  # Add frame to the queue

    def resolve_collisions(self):
        """Handle arbitration and collisions."""
        if len(self.current_transmissions) > 1:
            print(f"[CANBus] Collision detected among {len(self.current_transmissions)} nodes.")

            # Sort based on ID (lower ID wins)
            self.current_transmissions.sort(key=lambda x: x[0]['id'])
            winner_frame, winner_ecu = self.current_transmissions[0]
            active_error_flag = False

            for frame, ecu in self.current_transmissions:
                if frame != winner_frame:
                    # Check if IDs are identical, then compare DLC
                    if frame['id'] == winner_frame['id']:
                        # Compare DLC (dominant bit wins)
                        for bit_a, bit_b in zip(frame['dlc'], winner_frame['dlc']):
                            if bit_a != bit_b:
                                if bit_a == '0' and bit_b == '1':
                                    winner_frame, winner_ecu = frame, ecu
                                    active_error_flag = True
                                break

            for frame, ecu in self.current_transmissions:
                """The victim should transmit passive error flag"""
                if ecu.name == "Victim" and ecu.is_error_passive:
                    active_error_flag = False

            if active_error_flag:
                while not any(ecu.is_error_passive for _, ecu in self.current_transmissions if ecu.name == "Victim"):
                    # Trigger CAN bus error handling mechanism
                    for frame, ecu in self.current_transmissions:
                        if ecu.is_error_passive:
                            # Victim in Error-Passive: Transmit Passive Error Flag (111111)
                            if ecu.name == "Victim":
                                print(f"[{ecu.name}] In Error-Passive: Transmitting Passive Error Flag (111111).")
                        else:
                            # Victim in Error-Active: Transmit Active Error Flag (000000)
                            if ecu.name == "Victim":
                                print(f"[{ecu.name}] In Error-Active: Transmitting Active Error Flag (000000).")
                        
                        # Increment both TECs until the victim reaches error passive state
                        ecu.increment_error_counter(is_transmit_error=True)

                # Process attacker successful transmission
                print(f"[CANBus] Frame successfully transmitted: {winner_frame['id']} by {winner_ecu.name}")
                winner_ecu.decrement_error_counters()

                # Increment victim TEC due to successful attacker transmission
                for frame, ecu in self.current_transmissions:
                    if ecu.name == "Victim":
                        ecu.increment_error_counter(is_transmit_error=True)
                        ecu.decrement_error_counters()

                self.current_transmissions = []
                return winner_frame
            
            else:
                cont = 0

                # Trigger CAN bus error handling mechanism
                for frame, ecu in self.current_transmissions:
                    if ecu.name == "Victim":
                        # Victim in Error-Passive: Transmit Passive Error Flag (111111)
                        print(f"[{ecu.name}] In Error-Passive: Transmitting Passive Error Flag (111111).")
                        
                        ecu.increment_error_counter(is_transmit_error=True)
                        ecu.decrement_error_counters()
                    else:
                        frame, sender = self.current_transmissions.pop(cont)
                        print(f"[CANBus] Frame successfully transmitted: {frame['id']} by {sender.name}")
                        sender.decrement_error_counters()
                
                    cont += 1

                self.current_transmissions = []
                return frame
        
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
