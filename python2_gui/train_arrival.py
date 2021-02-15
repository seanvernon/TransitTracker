lines = {"Blue": "Blue", "G": "Green", "Red": "Red", "Org": "Orange", "Y": "Yellow",\
         "P": "Purple", "Brn": "Brown", "Pink": "Pink"}

class TrainArrival:
    def __init__(self, color, vin, destination, wait_time):
        
        self.line = lines[color]
        self.vin = vin
        self.destination = destination
        self.wait_time = wait_time
        self.color = lines[color]

    def info_string(self):
        return self.line+" Line #"+self.vin+" to"

    def __eq__(self, other):
        assert type(self) == type(other)
        return (self.line == other.line) and (self.vin == other.vin)  
