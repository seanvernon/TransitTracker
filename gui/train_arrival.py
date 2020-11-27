class TrainArrival:
    def __init__(self, line, vin, destination, wait_time):
        super().__init__()
        
        self.line = line
        self.vin = vin
        self.destination = destination
        self.wait_time = wait_time
        self.color = line

    def info_string(self):
        return f"{self.line} Line #{self.vin} to"
