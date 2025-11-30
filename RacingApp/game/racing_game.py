import pygame
import random

# ============================================================
#   GAME SETTINGS
# ============================================================
TOTAL_LAPS = 3
TRACK_LENGTH = 3000
TRACK_WIDTH = 800
TRACK_HEIGHT = 400

LANES = [-150, 0, 150]  # player + AI lanes
OBSTACLES = [100, 250, 400, 600]

pygame.init()
screen = pygame.display.set_mode((TRACK_WIDTH, TRACK_HEIGHT))
pygame.display.set_caption("3D Racing Game with Overtaking AI (Pixel Art)")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (20, 150, 20)
GRAY = (60, 60, 60)
SKY_BLUE = (135, 206, 235)
CLOUD_WHITE = (245, 245, 245)

# ============================================================
#   PERSPECTIVE PROJECTION
# ============================================================
def project_to_screen(world_x, dist, horizon=40):
    mid = TRACK_WIDTH // 2

    p = dist / TRACK_LENGTH
    p = max(0, min(1, p))

    y = horizon + p * (TRACK_HEIGHT - horizon)
    scale = 1 - 0.85 * p
    if scale < 0.15: scale = 0.15

    # fix: use scale for perspective but do not shrink toward road
    x = mid + world_x * scale

    return x, y, scale


# ============================================================
#   TELEMETRY
# ============================================================
class Telemetry:
    def __init__(self, total_laps):
        self.total_laps = total_laps
        self.lap_number = 1
        self.lap_time = 0
        self.start_time = pygame.time.get_ticks()
        self.speed = 0

    def update(self, speed):
        self.lap_time = round((pygame.time.get_ticks() - self.start_time) / 1000, 2)
        self.speed = speed

    def start_lap(self):
        self.lap_number += 1
        self.start_time = pygame.time.get_ticks()

# ============================================================
#   CAR
# ============================================================
class Car:
    def __init__(self, name, total_laps):
        self.name = name
        self.position = 0
        self.speed = 0
        self.lane_offset = 0
        self.telemetry = Telemetry(total_laps)

    def accelerate(self):
        self.speed += 5
        if self.speed > 60:
            self.speed = 60

    def brake(self):
        self.speed = max(0, self.speed - 8)

    def move(self):
        self.position += self.speed / 5
        if self.position > TRACK_LENGTH:
            self.position -= TRACK_LENGTH
            self.telemetry.start_lap()
        self.telemetry.update(self.speed)

# ============================================================
#   CAR IMAGE (Pixel Art)
# ============================================================
def create_3d_car(color):
    surf = pygame.Surface((60, 100), pygame.SRCALPHA)
    pygame.draw.polygon(surf, color, [(10, 90), (50, 90), (55, 20), (5, 20)])
    pygame.draw.ellipse(surf, (20, 20, 20), (0, 25, 15, 20))
    pygame.draw.ellipse(surf, (20, 20, 20), (45, 25, 15, 20))
    pygame.draw.ellipse(surf, (20, 20, 20), (0, 70, 15, 20))
    pygame.draw.ellipse(surf, (20, 20, 20), (45, 70, 15, 20))
    return surf

# ============================================================
#   SCENERY RIGHT NEXT TO ROAD
# ============================================================

ROAD_LEFT = -350
ROAD_RIGHT = 350

LEFT_EDGE  = ROAD_LEFT  - 80    # good position just off-road
RIGHT_EDGE = ROAD_RIGHT + 80

def next_to_left_road():
    return LEFT_EDGE

def next_to_right_road():
    return RIGHT_EDGE

def rand_dist():
    return random.randint(0, TRACK_LENGTH)

NUM_TREES = 16
NUM_BUSHES = 12
NUM_ROCKS = 8
NUM_SIGNS = 8
ROAD_LEFT_EDGE = -350
ROAD_RIGHT_EDGE = 350
SAFE_MARGIN = 50  # trees/signs will be at least 50px away from road edges

def generate_tree_x():
    # pick side: -1 = left, +1 = right
    side = random.choice([-1, 1])
    if side == -1:  # left side
        return random.randint(-900, ROAD_LEFT_EDGE - SAFE_MARGIN)
    else:  # right side
        return random.randint(ROAD_RIGHT_EDGE + SAFE_MARGIN, 900)

TREE_POSITIONS = [(generate_tree_x(), random.randint(0, TRACK_LENGTH)) for _ in range(NUM_TREES)]
BUSH_POSITIONS = [(generate_tree_x(), random.randint(0, TRACK_LENGTH)) for _ in range(NUM_BUSHES)]
ROCK_POSITIONS = [(generate_tree_x(), random.randint(0, TRACK_LENGTH)) for _ in range(NUM_ROCKS)]
SIGN_POSITIONS = [(generate_tree_x(), random.randint(0, TRACK_LENGTH)) for _ in range(NUM_SIGNS)]


CLOUDS = [{"x": random.randint(0, TRACK_WIDTH),
           "y": random.randint(10, 80),
           "speed": random.uniform(0.2, 0.6)} for _ in range(5)]

def draw_clouds():
    for c in CLOUDS:
        pygame.draw.ellipse(screen, CLOUD_WHITE, (c["x"], c["y"], 60, 30))
        c["x"] += c["speed"]
        if c["x"] > TRACK_WIDTH:
            c["x"] = -60

def draw_tree(xw, dist):
    x, y, s = project_to_screen(xw, dist)

    trunk_width = int(20 * s)
    trunk_height = int(60 * s)
    pygame.draw.rect(screen, (101, 67, 33),
                     (x - trunk_width//2, y - trunk_height, trunk_width, trunk_height))

    foliage_width = int(60 * s)
    foliage_height = int(60 * s)
    colors = [(34,139,34), (50,205,50), (0,128,0)]

    for i, col in enumerate(colors):
        pygame.draw.ellipse(screen, col,
            (x - foliage_width//2, y - trunk_height - foliage_height + int(i * 15 * s),
             foliage_width, foliage_height))

def draw_bush(xw, dist):
    x, y, s = project_to_screen(xw, dist)
    pygame.draw.ellipse(screen, (30, 120, 30), (x - 15 * s, y - 10 * s, 30 * s, 20 * s))

def draw_rock(xw, dist):
    x, y, s = project_to_screen(xw, dist)
    pygame.draw.ellipse(screen, (140, 140, 140), (x - 10 * s, y - 7 * s, 20 * s, 15 * s))

def draw_sign(xw, dist):
    x, y, s = project_to_screen(xw, dist)
    ph, pw = int(30*s), int(6*s)
    sh, sw = int(15*s), int(30*s)
    pygame.draw.rect(screen, (150, 75, 0), (x - pw // 2, y - ph, pw, ph))
    pygame.draw.rect(screen, (255, 0, 0), (x - sw // 2, y - ph - sh, sw, sh))

# ============================================================
#   ROAD + BACKGROUND
# ============================================================
def draw_road():
    mid = TRACK_WIDTH // 2
    horizon = 40
    TOP_W = 80
    BOT_W = 700

    screen.fill(SKY_BLUE)
    draw_clouds()
    pygame.draw.rect(screen, GREEN, (0, horizon, TRACK_WIDTH, TRACK_HEIGHT - horizon))

    pygame.draw.polygon(screen, GRAY, [
        (mid - TOP_W // 2, horizon),
        (mid + TOP_W // 2, horizon),
        (mid + BOT_W // 2, TRACK_HEIGHT),
        (mid - BOT_W // 2, TRACK_HEIGHT)
    ])

    pygame.draw.line(screen, WHITE, (mid - TOP_W // 2, horizon), (mid - BOT_W // 2, TRACK_HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (mid + TOP_W // 2, horizon), (mid + BOT_W // 2, TRACK_HEIGHT), 4)

    for i in range(25):
        if i % 2 == 0:
            p = i / 25
            y = horizon + p * (TRACK_HEIGHT - horizon)
            pygame.draw.line(screen, WHITE, (mid, y), (mid, y + 6), 4)

# ============================================================
#   AI CONTROLLER
# ============================================================
class AIController:
    def __init__(self, base_lane):
        self.base_lane = base_lane
        self.target_lane = base_lane
        self.cooldown = 0
        self.state = "CRUISE"

    def detect_car_ahead(self, car, all_cars):
        for o in all_cars:
            if o is car: continue
            if abs(o.lane_offset - car.lane_offset) < 40:
                if 0 < o.position - car.position < 70:
                    return o
        return None

    def pick_other_lane(self):
        if self.base_lane == LANES[0]:
            return LANES[1]
        elif self.base_lane == LANES[2]:
            return LANES[1]
        return random.choice([LANES[0], LANES[2]])

    def update(self, car, all_cars):
        if self.cooldown > 0:
            self.cooldown -= 1

        slow_car = self.detect_car_ahead(car, all_cars)

        if slow_car and self.cooldown == 0:
            self.state = "OVERTAKE"
            self.target_lane = self.pick_other_lane()

        elif slow_car and abs(car.position - slow_car.position) > 70:
            self.state = "RETURN"
            self.target_lane = self.base_lane

        else:
            self.state = "CRUISE"

        if self.state == "CRUISE":
            if car.speed < 45:
                car.accelerate()
            else:
                car.brake()

        elif self.state == "OVERTAKE":
            car.accelerate()
            if abs(car.lane_offset - self.target_lane) < 4:
                car.lane_offset = self.target_lane
            elif self.target_lane > car.lane_offset:
                car.lane_offset += 4
            else:
                car.lane_offset -= 4
            self.cooldown = 50

        elif self.state == "RETURN":
            if abs(car.lane_offset - self.target_lane) < 4:
                car.lane_offset = self.target_lane
            elif self.target_lane > car.lane_offset:
                car.lane_offset += 4
            else:
                car.lane_offset -= 4

# ============================================================
#   PLAYER NAME + START COUNTDOWN
# ============================================================
def get_player_name():
    font = pygame.font.SysFont(None, 48)
    name = ""
    while True:
        screen.fill(WHITE)
        txt = font.render(f"Enter Your Name: {name}", True, BLACK)
        screen.blit(txt, (100, 150))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name:
                    return name
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += e.unicode

def start_countdown():
    font = pygame.font.SysFont(None, 100)
    for n in ["3", "2", "1", "GO!"]:
        screen.fill(WHITE)
        t = font.render(n, True, (200, 0, 0))
        r = t.get_rect(center=(TRACK_WIDTH // 2, TRACK_HEIGHT // 2))
        screen.blit(t, r)
        pygame.display.flip()
        pygame.time.delay(1000)

# ============================================================
#   GAME INIT
# ============================================================
player_name = get_player_name()
player = Car(player_name, TOTAL_LAPS)
ai1 = Car("AI_1", TOTAL_LAPS)
ai2 = Car("AI_2", TOTAL_LAPS)

player.lane_offset = LANES[1]
ai1.lane_offset = LANES[0]
ai2.lane_offset = LANES[2]

controllers = [AIController(LANES[0]), AIController(LANES[2])]
all_cars = [player, ai1, ai2]

player_img = create_3d_car((255, 255, 0))
ai_imgs = [create_3d_car((200, 0, 0)), create_3d_car((0, 0, 255))]

font = pygame.font.SysFont(None, 24)
start_countdown()

# ============================================================
#   MAIN LOOP
# ============================================================
running = True
winner = None

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.accelerate()
    if keys[pygame.K_s]: player.brake()
    if keys[pygame.K_a]: player.lane_offset -= 4
    if keys[pygame.K_d]: player.lane_offset += 4

    player.lane_offset = max(LANES[0], min(LANES[2], player.lane_offset))

    if keys[pygame.K_a] or keys[pygame.K_d]:
        nearest = min(LANES, key=lambda x: abs(x - player.lane_offset))
        if abs(player.lane_offset - nearest) < 4:
            player.lane_offset = nearest

    player.move()

    for ctrl, ai in zip(controllers, [ai1, ai2]):
        ctrl.update(ai, all_cars)
        ai.move()

    for car in all_cars:
        for obs in OBSTACLES:
            if car.position < obs <= car.position + car.speed / 5:
                car.brake()

    for car in all_cars:
        if car.telemetry.lap_number > TOTAL_LAPS:
            winner = car
            running = False
            break

    draw_road()

    for xw, pos in TREE_POSITIONS:
        draw_tree(xw, (pos - player.position) % TRACK_LENGTH)

    for xw, pos in BUSH_POSITIONS:
        draw_bush(xw, (pos - player.position) % TRACK_LENGTH)

    for xw, pos in ROCK_POSITIONS:
        draw_rock(xw, (pos - player.position) % TRACK_LENGTH)

    for xw, pos in SIGN_POSITIONS:
        draw_sign(xw, (pos - player.position) % TRACK_LENGTH)

    for car, img in [(player, player_img), (ai1, ai_imgs[0]), (ai2, ai_imgs[1])]:
        x, y, s = project_to_screen(car.lane_offset, car.position)
        w, h = img.get_size()
        scaled = pygame.transform.scale(img, (int(w * s), int(h * s)))
        rect = scaled.get_rect(center=(x, y))
        screen.blit(scaled, rect)

    screen.blit(font.render(f"{player.name} Lap {player.telemetry.lap_number}/{TOTAL_LAPS} Speed {int(player.speed)}", True, BLACK), (10, 10))
    screen.blit(font.render(f"AI_1 Speed {int(ai1.speed)}", True, BLACK), (10, 30))
    screen.blit(font.render(f"AI_2 Speed {int(ai2.speed)}", True, BLACK), (10, 50))

    pygame.display.flip()
    clock.tick(30)

screen.fill(WHITE)
font_big = pygame.font.SysFont(None, 80)
text = font_big.render(f"{winner.name} WINS!", True, (200, 0, 0))
rect = text.get_rect(center=(TRACK_WIDTH // 2, TRACK_HEIGHT // 2))
screen.blit(text, rect)
pygame.display.flip()
pygame.time.delay(5000)

pygame.quit()
