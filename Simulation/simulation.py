from can_bus import CANBus
from victim_ecu import VictimECU
from attacker_ecu import AttackerECU
from setup_logger import logger

def simulate_bus_off_attack():
    bus = CANBus()
    victim = VictimECU("Victim", bus)
    attacker = AttackerECU("Attacker", bus)

    # Phase 1: Pattern Analysis
    traffic = []
    step = 100  # every x ms a frame is sent
    time_interval = 10000 
    periodic_frame_interval = 500 # periodicity of the frame
    
    for current_time_ms in range(0, time_interval, step):  # Simulate frame tx every 
        if (current_time_ms + step) % periodic_frame_interval == 0:
            victim.send_preceded_frame()  # Send the preceded frame
        elif current_time_ms % periodic_frame_interval == 0:
            victim.send_periodic_frame()  # Send the periodic frame
        else:
            victim.send_non_periodic_frame()  # Send a non-periodic frame

        # Process bus traffic
        result = bus.receive_frame()
        if result:
            frame = result  # Get the frame and add to traffic
            traffic.append(frame)  
        else:
            print("[Simulation] No frames available at this time step.")

    # Phase 2: Attack Execution
    attacker.analyze_pattern(traffic)

    if attacker.target_pattern:
        attacker.execute_attack(victim)
        if victim.is_bus_off:
            print("[Simulation] Victim has entered bus-off state.")
    else:
        print("[Simulation] No valid pattern identified; attack aborted.")


for i in range(1,1001):
    print(f"Executing the attack for the {i}-th time:")
    simulate_bus_off_attack()
    logger.debug(f"End of the {i}-th attack")

