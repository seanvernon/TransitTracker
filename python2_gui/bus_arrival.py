class BusArrival:
    def __init__(self, line, direction, destination, wait_time):
        
        self.line = line
        self.direction = direction
        self.destination = destination
        self.wait_time = wait_time
        self.color = "Grey"

    def info_string(self):
        return "#"+self.line+" Bus "+self.direction+" to"
