import time

class Telemetry:
    def __init__(self, total_laps=3):
        self.total_laps = total_laps
        self.lap_number = 0
        self.lap_time = 0.0
        self.start_time = None
        self.speed = 0.0
        self.rpm = 0

    def start_lap(self):
        self.start_time = time.time()
        self.lap_time = 0.0
        self.lap_number += 1

    def update(self, car_speed):
        self.speed = round(car_speed, 1)
        self.rpm = int(car_speed * 50)
        if self.start_time:
            self.lap_time = round(time.time() - self.start_time, 2)

    def get_data(self):
        return {
            "speed": self.speed,
            "rpm": self.rpm,
            "lap_time": self.lap_time,
            "lap_number": self.lap_number
        }

    def is_race_finished(self):
        return self.lap_number > self.total_laps
