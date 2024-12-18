import random
import cantools
import csv
import os

# -------------------------
# Configurations
# -------------------------
DBC_FILE = "dbc/ford_lincoln_base_pt.dbc"  # Replace with your DBC file path
OUTPUT_DIR = "generated_logs"  # Folder to store output files
LOG_COUNT = 1000  # Number of logs to generate per file
FILE_COUNT = 10  # Number of output files to generate
PATTERN_PROBABILITY = 0.1  # 10% chance for a pattern to be included in a file

# Logical patterns based on related arbitration IDs
"""
    Tire Pressure Messages:
    BO_ 949 Tire_Pressure_Data_FD1 -> 0x3B5
    BO_ 524 AWD_Torque_Data -> 0x20C
    BO_ 570 Suspension_Data -> 0x23A

    Energy Management and Charging:
    BO_ 740 PHEV_Battery_Data1_FD1 -> 0x2E4
    BO_ 1142 ConsTip_Data_FD1 -> 0x476
    BO_ 850 HEV_ChargeStat_FD1 -> 0x352
    BO_ 1160 ECG_Data2_FD1 -> 0x488

    Trailer Control and Monitoring:
    BO_ 1114 TrailerAid_Data_FD1 -> 0x45A
    BO_ 1116 TrailerAid_Data3_FD1 -> 0x45C
    BO_ 1106 TrailerAid_Stat1_FD1 -> 0x452
"""
LOGICAL_PATTERNS = [
    [949, 524, 570],  # Tire Pressure Messages
    [740, 1142, 850, 1160],  # Energy Management and Charging
    [1114, 1116, 1106],  # Trailer Control and Monitoring
]

# -------------------------
# Load the DBC file
# -------------------------
try:
    db = cantools.database.load_file(DBC_FILE)
    print("DBC file loaded successfully!")
except Exception as e:
    print(f"Error loading DBC file: {e}")
    exit(1)

# Get all valid messages
all_messages = db.messages  # List of all messages
valid_message_ids = {message.frame_id: message for message in all_messages}
print(f"Loaded {len(all_messages)} messages. Valid arbitration IDs: {len(valid_message_ids)}")

# -------------------------
# Function to generate random data for a message
# -------------------------
def generate_random_data(message):
    """
    Generates consistent random signal values within the range defined in the DBC file.
    """
    data = {}
    for signal in message.signals:
        min_value = signal.minimum if signal.minimum is not None else 0
        max_value = signal.maximum if signal.maximum is not None else 1
        scale = signal.scale if signal.scale else 1.0
        offset = signal.offset if signal.offset else 0.0

        raw_min = (min_value - offset) / scale
        raw_max = (max_value - offset) / scale

        if signal.is_float:
            value = round(random.uniform(raw_min, raw_max), 4)  # Floating-point signal
        else:
            raw_min_int = int(raw_min) if signal.is_signed else max(0, int(raw_min))
            raw_max_int = int(raw_max)
            value = random.randint(raw_min_int, raw_max_int)

        final_value = value * scale + offset
        final_value = max(min(final_value, max_value), min_value)  # Ensure within bounds
        data[signal.name] = final_value
    return data

# -------------------------
# Generate CAN logs
# -------------------------
output_dir = OUTPUT_DIR
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file_index in range(FILE_COUNT):
    logs = []

    # Decide if this file will include a pattern
    include_pattern = random.random() < PATTERN_PROBABILITY
    if include_pattern:
        # Choose a random pattern to include
        selected_pattern = random.choice(LOGICAL_PATTERNS)
        for arbitration_id in selected_pattern:
            if arbitration_id in valid_message_ids:
                message = valid_message_ids[arbitration_id]
                try:
                    signal_data = generate_random_data(message)
                    data_bytes = message.encode(signal_data)  # Encode data into CAN frame
                    logs.append((arbitration_id, len(data_bytes), data_bytes.hex()))
                except Exception as e:
                    print(f"Error encoding data for message {message.name} (ID: {hex(arbitration_id)}): {e}")

    # Generate the remaining logs, which may or may not contain pattern IDs
    for _ in range(LOG_COUNT - len(logs)):
        message = random.choice(all_messages)
        arbitration_id = message.frame_id
        try:
            signal_data = generate_random_data(message)
            data_bytes = message.encode(signal_data)  # Encode data into CAN frame
            logs.append((arbitration_id, len(data_bytes), data_bytes.hex()))
        except Exception as e:
            print(f"Error encoding data for message {message.name} (ID: {hex(arbitration_id)}): {e}")

    # Write the logs to a CSV file
    output_file = os.path.join(output_dir, f"generated_logs_{file_index + 1}.csv")
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Arbitration_ID", "DLC", "Data"])
        for log in logs:
            writer.writerow([hex(log[0]), log[1], log[2]])

    print(f"Generated {len(logs)} logs and saved to '{output_file}'.")
