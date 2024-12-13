# Bus-Off Attack Simulation

**A project for the Cyber-Physical Systems and IoT Security course - MSc Computer Science - University of Padova.**

This repository simulates a Bus-Off attack on a CAN (Controller Area Network) bus, showcasing the dynamics of error handling and frame arbitration in a vehicle communication system. The attack is aimed at forcing a victim ECU (Electronic Control Unit) into a bus-off state, rendering it incapable of communication.

## Project Structure

### 1. **Files Overview**

#### **`can_bus.py`**
- Implements the `CANBus` class to simulate the shared communication medium.
- Handles frame arbitration and collision resolution.
- Implements error-handling mechanisms, including TEC (Transmit Error Counter) increments and error flag emission.

#### **`ecu.py`**
- Implements the base `ECU` class.
- Contains methods for transmitting (`send`) and receiving (`listen`) frames.
- Manages error counters and state transitions (Error-Active, Error-Passive, Bus-Off).

#### **`victim_ecu.py`**
- Extends the `ECU` class to represent the victim node.
- Sends periodic, preceded, and non-periodic frames to simulate normal communication.

#### **`attacker_ecu.py`**
- Extends the `ECU` class to represent the attacker node.
- Identifies transmission patterns using `analyze_pattern`.
- Executes the Bus-Off attack by exploiting arbitration and error-handling logic.

#### **`simulation.py`**
- Orchestrates the simulation.
- Initializes the CAN bus, victim, and attacker ECUs.
- Runs the two main phases of the attack: **Pattern Analysis** and **Attack Execution**.

### 2. **Key Classes**

#### **`CANBus`**
- Tracks current transmissions on the bus.
- Resolves collisions based on ID and DLC (Data Length Code) priority.
- Implements the error-handling mechanism to simulate real-world CAN behavior.

#### **`ECU`**
- Base class representing any node on the CAN bus.
- Manages state transitions and error counters (TEC and REC).

#### **`VictimECU`**
- Periodically transmits frames to simulate normal behavior.
- Includes logic for sending different types of messages (preceded, periodic, non-periodic).

#### **`AttackerECU`**
- Observes CAN traffic to identify patterns in victim ECU transmissions.
- Launches a synchronized attack to exploit CAN arbitration and error recovery mechanisms.

## How It Works

### 1. **Simulation Phases**

#### **Phase 1: Pattern Analysis**
- The attacker listens to CAN traffic and identifies a pattern where a periodic frame is always preceded by a specific frame.
- This pattern helps the attacker predict when to inject a malicious frame during the attack.

#### **Phase 2: Attack Execution**
- The attacker injects a fabricated frame at the same time the victim transmits a periodic message.
- Collisions are resolved using arbitration:
  - Frames with lower IDs win.
  - If IDs are identical, DLC is compared (dominant bits win).
- TECs of both nodes are incremented for each failed transmission.
- The victim transitions to `Error-Passive`, and the attacker continues transmitting until the victim enters `Bus-Off`.

### 2. **CAN Bus Error Handling**
- **Error-Active:** TEC > 127; Active Error Flag (`000000`) is transmitted.
- **Error-Passive:** TEC > 255; Passive Error Flag (`111111`) is transmitted.
- **Bus-Off:** TEC > 255; ECU stops communication.

### 3. **Key Attack Dynamics**
- The victim’s TEC increases by 8 for each failed transmission.
- The attacker’s TEC also increases but is reduced by 1 after successful transmissions.
- Once the victim transitions to `Error-Passive`, its error flags can no longer disrupt the attacker’s transmissions.

## Running the Simulation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd Bus-Off-Attack-Simulation
   ```

2. Run the simulation:
   ```bash
   python simulation.py
   ```

3. Observe the output, including:
   - Pattern identification by the attacker.
   - Incrementing TEC values.
   - Victim transitioning through Error-Active, Error-Passive, and Bus-Off states.

## Example Output
```plaintext
[Attacker] Identified pattern: Precedent ID 0000100000 followed by Periodic ID 0001000000.
[Victim] Sending frame: {'id': '0001000000', 'dlc': '0001', 'data': ['00000000']}
[Attacker] Detected preceded frame: 0000100000. Preparing attack frame.
[CANBus] Collision detected among 2 nodes.
[Victim] In Error-Active: Transmitting Active Error Flag (000000).
[Attacker] TEC incremented due to victim's active error flag.
[Victim] Entered Error-Passive state.
[CANBus] Frame successfully transmitted: 0001000000 by Attacker.
[Simulation] Victim has entered Bus-Off state.
```

## Acknowledgments

This simulation demonstrates the nuances of CAN bus behavior during a Bus-Off attack and highlights the importance of robust error-handling mechanisms in automotive security.
