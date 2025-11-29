from RacingApp.telemetry.telemetry import Telemetry

class Car:
    def __init__(self, name, total_laps):
        self.name = name
        self.position = 0.0
        self.speed = 0.0

        # Physics settings
        self.max_speed = 120
        self.acceleration = 3
        self.brake_force = 5
        self.friction = 0.2

        # Telemetry
        self.telemetry = Telemetry(total_laps=total_laps)
        self.telemetry.start_lap()

    def accelerate(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def brake(self):
        self.speed = max(0, self.speed - self.brake_force)


    def move(self):
        if self.speed > 0:
            self.speed -= self.friction
        if self.speed < 0:
            self.speed = 0

        self.position += self.speed * 0.2

        self.telemetry.update(self.speed)
