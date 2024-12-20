from setup_logger import logger
class ECU:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
        self.transmit_error_counter = 0
        self.is_error_passive = False
        self.is_bus_off = False
        logger.debug(f"ECU's name: {self.name}'s TEC value: {self.transmit_error_counter} Passive error state: {self.is_error_passive} Bus-off state: {self.is_bus_off}")

    def send(self, frame):
        """Transmit a CAN frame."""
        if self.is_bus_off:
            print(f"[{self.name}] Cannot send; ECU is in Bus-off state!")
            return

        print(f"[{self.name}] Sending frame: {frame}")
        self.bus.send_frame(frame, self)

    def listen(self):
        """Listen for a frame on the CAN bus."""
        if self.is_bus_off:
            return

        result = self.bus.receive_frame()
        if result:
            frame, sender = result
            if sender != self:
                print(f"[{self.name}] Received frame: {frame}")

    def increment_error_counter(self, is_transmit_error):
        """Increment the error counter."""
        increment = 8 if is_transmit_error else 0
        self.transmit_error_counter += increment
        logger.debug(f"ECU's name: {self.name}'s TEC value: {self.transmit_error_counter} Passive error state: {self.is_error_passive} Bus-off state: {self.is_bus_off}")

        print(f"[{self.name}] Incremented {'Transmit' if is_transmit_error else 'Receive'} Error Counter. "
              f"TEC: {self.transmit_error_counter}")

        if not self.is_error_passive and self.transmit_error_counter > 127:
            self.is_error_passive = True
            print(f"[{self.name}] Entered Error-Passive state.")
        if self.transmit_error_counter > 255:
            self.is_bus_off = True
            print(f"[{self.name}] Entered Bus-Off state!")

    def decrement_error_counters(self):
        """Reduce error counters after successful operations."""
        self.transmit_error_counter = max(0, self.transmit_error_counter - 1)
        logger.debug(f"ECU's name: {self.name}'s TEC value: {self.transmit_error_counter} Passive error state: {self.is_error_passive} Bus-off state: {self.is_bus_off}")

        if self.is_error_passive and self.transmit_error_counter <= 127:
            self.is_error_passive = False
            print(f"[{self.name}] Entered Error-Active state.")
