class Arrival:

    def __init__(self, station_name, line, stop_desc, wait_time):

        self.station_name = station_name
        self.line = line
        self.stop_desc = stop_desc
        self.wait_time = wait_time

    # Returns a string representing this arrival object.
    def __str__(self):
        wait_string = f"{self.wait_time} minutes" if self.wait_time > 1 else "Due"
        return f"{self.station_name}\n{self.line} Line {self.stop_desc}\n{wait_string}\n"
