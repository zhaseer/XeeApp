import random
import pygame
import os

# --- Game settings ---
TOTAL_LAPS = 3
TRACK_LENGTH = 800  # increased from 400
TRACK_WIDTH = 800
TRACK_HEIGHT = 400
OBSTACLES = [100, 250, 400, 600]  # spaced out more for longer track
LANE_OFFSET_AI = [-100, 100]  # Spread for AI cars

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((TRACK_WIDTH, TRACK_HEIGHT))
pygame.display.set_caption("3D Racing Game with Scaling Perspective")
clock = pygame.time.Clock()


# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
DARK_GRAY = (30, 30, 30)

# =========================
# --- Telemetry Class ---
# =========================
class Telemetry:
    def __init__(self, total_laps=3):
        self.total_laps = total_laps
        self.lap_number = 0
        self.lap_time = 0
        self.start_time = None
        self.speed = 0

    def start_lap(self):
        self.start_time = pygame.time.get_ticks()
        self.lap_time = 0
        self.lap_number += 1

    def update(self, current_speed):
        self.speed = current_speed
        if self.start_time:
            self.lap_time = round((pygame.time.get_ticks() - self.start_time) / 1000, 2)

# =========================
# --- Car Class ---
# =========================
class Car:
    def __init__(self, name, total_laps):
        self.name = name
        self.position = 0
        self.speed = 0
        self.telemetry = Telemetry(total_laps)
        self.telemetry.start_lap()

    def accelerate(self):
        self.speed += 6  # slightly faster for longer track
        if self.speed > 60:
            self.speed = 60

    def brake(self):
        self.speed = max(0, self.speed - 6)

    def move(self):
        self.position += self.speed / 5
        if self.position > TRACK_LENGTH:
            self.position = TRACK_LENGTH
        self.telemetry.update(self.speed)

# =========================
# --- Car Drawing ---
# =========================
def create_3d_car_surface(color=(200, 0, 0)):
    car_surface = pygame.Surface((60, 30), pygame.SRCALPHA)
    car_surface.fill((0, 0, 0, 0))
    for i in range(30):
        shade = max(min(255, color[0] - i*3), 0)
        pygame.draw.line(car_surface, (shade, 0, 0), (0, i), (60, i))
    pygame.draw.rect(car_surface, (50,50,50), (15,8,30,14), border_radius=4)
    pygame.draw.ellipse(car_surface, (255,255,180), (2,7,6,6))
    pygame.draw.ellipse(car_surface, (255,255,180), (2,17,6,6))
    pygame.draw.ellipse(car_surface, (200,0,0), (52,7,6,6))
    pygame.draw.ellipse(car_surface, (200,0,0), (52,17,6,6))
    pygame.draw.ellipse(car_surface, DARK_GRAY, (10,3,8,14))
    pygame.draw.ellipse(car_surface, DARK_GRAY, (42,3,8,14))
    return car_surface

def add_motion_blur(surface, speed):
    blur_length = int(min(speed // 2, 15))
    if blur_length <= 1:
        return surface
    blur_surface = surface.copy()
    for i in range(1, blur_length):
        alpha = max(1, 150 - i*10)
        temp = surface.copy()
        temp.set_alpha(alpha)
        blur_surface.blit(temp, (-i, 0))
    return blur_surface

def rotate_car(image, speed, x, y):
    angle = -speed*2
    rotated = pygame.transform.rotate(image, angle)
    rect = rotated.get_rect(center=(x, y))
    return rotated, rect

def scale_car_image(car_img, distance):
    scale_factor = 0.5 + 0.5 * (distance / TRACK_LENGTH)
    w, h = car_img.get_size()
    new_size = (max(10, int(w*scale_factor)), max(5, int(h*scale_factor)))
    return pygame.transform.scale(car_img, new_size)

# =========================
# --- Perspective Track ---
# =========================
def draw_perspective_track():
    mid_x = TRACK_WIDTH//2
    horizon = 50
    track_top_width = 100
    track_bottom_width = 700
    num_lines = 30
    for i in range(num_lines):
        progress = i / num_lines
        y = horizon + progress*(TRACK_HEIGHT - horizon)
        width = track_top_width + progress*(track_bottom_width - track_top_width)
        pygame.draw.rect(screen, DARK_GRAY, (mid_x - width//2, y, width, 5))

# =========================
# --- Helper Functions ---
# =========================
def check_lap(car):
    if car.position >= TRACK_LENGTH:
        car.position = 0
        car.telemetry.start_lap()

def display_winner(name):
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"{name} Wins!", True, RED)
    screen.blit(text, (TRACK_WIDTH//2 - 100, TRACK_HEIGHT//2 - 24))
    pygame.display.flip()
    pygame.time.delay(3000)

# --- Countdown Before Race ---
def start_lights():
    font = pygame.font.SysFont(None, 72)
    countdown_numbers = ["3", "2", "1", "GO!"]
    for number in countdown_numbers:
        screen.fill(WHITE)
        text = font.render(number, True, RED)
        rect = text.get_rect(center=(TRACK_WIDTH//2, TRACK_HEIGHT//2))
        screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.delay(1000)

# --- Get Player Name ---
def get_player_name():
    font = pygame.font.SysFont(None, 48)
    name = ""
    entering = True
    while entering:
        screen.fill(WHITE)
        prompt = font.render("Enter Your Name: " + name, True, BLACK)
        rect = prompt.get_rect(center=(TRACK_WIDTH//2, TRACK_HEIGHT//2))
        screen.blit(prompt, rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip() != "":
                    entering = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12:  # limit name length
                        name += event.unicode
    return name

# =========================
# --- Initialize Game ---
# =========================
player_name = get_player_name()
player_car = Car(player_name, TOTAL_LAPS)
ai_cars = [Car(f"AI_{i+1}", TOTAL_LAPS) for i in range(2)]

player_img = create_3d_car_surface(RED)
ai_imgs = [create_3d_car_surface(BLUE), create_3d_car_surface(GREEN)]

player_lane_offset = 0
winner_declared = False

# --- Start Countdown ---
start_lights()

# =========================
# --- Main Game Loop ---
# =========================
running = True
while running:
    screen.fill(WHITE)

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Player Controls ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_car.accelerate()
    if keys[pygame.K_s]:
        player_car.brake()
    if keys[pygame.K_a]:
        player_lane_offset = max(-60, player_lane_offset - 5)
    if keys[pygame.K_d]:
        player_lane_offset = min(60, player_lane_offset + 5)

    player_car.move()

    # --- AI Movement ---
    for i, ai in enumerate(ai_cars):
        next_obs = min((obs for obs in OBSTACLES if obs > ai.position), default=TRACK_LENGTH)
        if next_obs - ai.position < 10:
            ai.brake()
        else:
            if random.random() > 0.2:
                ai.accelerate()
            else:
                ai.brake()
        ai.move()

    # --- Obstacles ---
    for car in [player_car] + ai_cars:
        for obs in OBSTACLES:
            if abs(car.position - obs) < 3:
                car.speed = max(0, car.speed - 10)

    # --- Draw Track ---
    draw_perspective_track()

    # --- Draw Player Car ---
    distance_player = TRACK_LENGTH - player_car.position
    player_x = TRACK_WIDTH//2 + player_lane_offset
    player_y = 50 + (distance_player / TRACK_LENGTH) * (TRACK_HEIGHT - 50)  # adjusted for longer track
    blurred_player = add_motion_blur(player_img, player_car.speed)
    player_scaled = scale_car_image(blurred_player, distance_player)
    player_rot, player_rect = rotate_car(player_scaled, player_car.speed, player_x, player_y)
    screen.blit(player_rot, player_rect)

    # --- Draw AI Cars ---
    for i, ai in enumerate(ai_cars):
        distance_ai = TRACK_LENGTH - ai.position
        ai_x = TRACK_WIDTH//2 + LANE_OFFSET_AI[i]
        ai_y = 50 + (distance_ai / TRACK_LENGTH) * (TRACK_HEIGHT - 50)
        blurred_ai = add_motion_blur(ai_imgs[i], ai.speed)
        ai_scaled = scale_car_image(blurred_ai, distance_ai)
        ai_rot, ai_rect = rotate_car(ai_scaled, ai.speed, ai_x, ai_y)
        screen.blit(ai_rot, ai_rect)

    # --- Telemetry ---
    font = pygame.font.SysFont(None, 24)
    screen.blit(font.render(f"{player_car.name} Lap: {player_car.telemetry.lap_number}/{TOTAL_LAPS} Speed: {int(player_car.speed)}", True, BLACK), (10, 10))
    for i, ai in enumerate(ai_cars):
        screen.blit(font.render(f"{ai.name} Lap: {ai.telemetry.lap_number}/{TOTAL_LAPS} Speed: {int(ai.speed)}", True, BLACK), (10, 30 + i*20))

    # --- Lap Checks ---
    check_lap(player_car)
    for ai in ai_cars:
        check_lap(ai)

    # --- Check Winner ---
    if not winner_declared:
        for car in [player_car] + ai_cars:
            if car.telemetry.lap_number > TOTAL_LAPS:
                display_winner(car.name)
                winner_declared = True
                running = False
                break

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
