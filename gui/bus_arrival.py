class BusArrival:
    def __init__(self, line, direction, destination, wait_time):
        super().__init__()
        
        self.line = line
        self.direction = direction
        self.destination = destination
        self.wait_time = wait_time
        self.color = "Grey"

    def info_string(self):
        return f"#{self.line} Bus {self.direction} to"
