import pygame
import random
import math

# ============================================================
#   GAME SETTINGS
# ============================================================
TOTAL_LAPS = 3
TRACK_LENGTH = 800
TRACK_WIDTH = 800
TRACK_HEIGHT = 400

LANES = [-150, 0, 150]  # player + AI lane offsets inside the road
OBSTACLES = [100, 250, 400, 600]

pygame.init()
screen = pygame.display.set_mode((TRACK_WIDTH, TRACK_HEIGHT))
pygame.display.set_caption("3D Racing Game with Overtaking AI (Pixel Art)")
clock = pygame.time.Clock()

WHITE=(255,255,255)
BLACK=(0,0,0)
GREEN=(20,150,20)
GRAY=(60,60,60)
SKY_BLUE=(135,206,235)
CLOUD_WHITE=(245,245,245)

# ============================================================
#   PERSPECTIVE PROJECTION (REAL FIX)
# ============================================================
def project_to_screen(world_x, dist, horizon=40):
    """
    Convert world coordinates (world_x, dist)
    into perspective-correct (x, y, scale).
    """
    mid = TRACK_WIDTH // 2
    TOP_W = 80
    BOT_W = 700

    p = dist / TRACK_LENGTH
    if p < 0: p = 0
    if p > 1: p = 1

    y = horizon + p * (TRACK_HEIGHT - horizon)
    road_half_w = (TOP_W/2)*p + (BOT_W/2)*(1-p)

    # convert horizontal world position to screen X
    x = mid + world_x * (road_half_w / (BOT_W/2))

    scale = 1 - 0.85 * p
    if scale < 0.15:
        scale = 0.15

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

    def update(self, speed):
        self.lap_time = round((pygame.time.get_ticks()-self.start_time)/1000,2)
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
            self.position = TRACK_LENGTH
        self.telemetry.update(self.speed)


# ============================================================
#   CAR IMAGE (Pixel Art)
# ============================================================
def create_3d_car(color):
    surf = pygame.Surface((60,100), pygame.SRCALPHA)
    pygame.draw.polygon(surf, color, [(10,90),(50,90),(55,20),(5,20)])
    pygame.draw.ellipse(surf, (20,20,20), (0,25,15,20))
    pygame.draw.ellipse(surf, (20,20,20), (45,25,15,20))
    pygame.draw.ellipse(surf, (20,20,20), (0,70,15,20))
    pygame.draw.ellipse(surf, (20,20,20), (45,70,15,20))
    return surf


# ============================================================
#   SCENERY GENERATION (REAL WORLD SPACE)
# ============================================================
LEFT_SIDE = (-400, -300)
RIGHT_SIDE = (300, 400)

def random_side_x():
    return random.choice([
        random.randint(*LEFT_SIDE),
        random.randint(*RIGHT_SIDE)
    ])

# ===========================
#  PIXEL ART TREES, BUSHES, ROCKS, SIGNS (FIXED)
# ===========================

NUM_TREES = 16
NUM_BUSHES = 12
NUM_ROCKS = 8
NUM_SIGNS = 8

TREE_POSITIONS = []
BUSH_POSITIONS = []
ROCK_POSITIONS = []
SIGN_POSITIONS = []

# Road visual width near camera ≈ 700px (half ≈ 350)
# Keep scenery WELL outside road: use ±600 to ±900 horizontal offsets

LEFT_SCENERY_X  = (-900, -600)
RIGHT_SCENERY_X = (600, 900)

def rand_left():  return random.randint(*LEFT_SCENERY_X)
def rand_right(): return random.randint(*RIGHT_SCENERY_X)

# --- Trees ---
for _ in range(NUM_TREES // 2):
    TREE_POSITIONS.append((rand_left(),  random.randint(0, TRACK_LENGTH)))
    TREE_POSITIONS.append((rand_right(), random.randint(0, TRACK_LENGTH)))

# --- Bushes ---
for _ in range(NUM_BUSHES // 2):
    BUSH_POSITIONS.append((rand_left(),  random.randint(0, TRACK_LENGTH)))
    BUSH_POSITIONS.append((rand_right(), random.randint(0, TRACK_LENGTH)))

# --- Rocks ---
for _ in range(NUM_ROCKS // 2):
    ROCK_POSITIONS.append((rand_left(),  random.randint(0, TRACK_LENGTH)))
    ROCK_POSITIONS.append((rand_right(), random.randint(0, TRACK_LENGTH)))

# --- Signs ---
for _ in range(NUM_SIGNS // 2):
    SIGN_POSITIONS.append((rand_left(),  random.randint(0, TRACK_LENGTH)))
    SIGN_POSITIONS.append((rand_right(), random.randint(0, TRACK_LENGTH)))


# clouds
CLOUDS = [{"x": random.randint(0, TRACK_WIDTH),
           "y": random.randint(10, 80),
           "speed": random.uniform(0.2,0.6)} for _ in range(5)]


# ============================================================
#   DRAW SCENERY
# ============================================================
def draw_clouds():
    for c in CLOUDS:
        pygame.draw.ellipse(screen, CLOUD_WHITE, (c["x"], c["y"], 60, 30))
        c["x"] += c["speed"]
        if c["x"] > TRACK_WIDTH:
            c["x"] = -60

def draw_tree(xw, dist):
    x,y,s = project_to_screen(xw, dist)
    th = int(40*s)
    tw = int(8*s)
    fh = int(60*s)
    fw = int(60*s)

    pygame.draw.rect(screen,(95,65,35),(x-tw//2,y-th,tw,th))
    pygame.draw.rect(screen,(40,150,40),(x-fw//2,y-th-fh,fw,fh))

def draw_bush(xw, dist):
    x,y,s = project_to_screen(xw, dist)
    w = int(30*s); h = int(20*s)
    pygame.draw.ellipse(screen,(30,120,30),(x-w//2,y-h,w,h))

def draw_rock(xw, dist):
    x,y,s = project_to_screen(xw, dist)
    w = int(20*s); h = int(15*s)
    pygame.draw.ellipse(screen,(140,140,140),(x-w//2,y-h,w,h))

def draw_sign(xw, dist):
    x,y,s = project_to_screen(xw, dist)
    ph=int(30*s); pw=int(6*s)
    sh=int(15*s); sw=int(30*s)
    pygame.draw.rect(screen,(150,75,0),(x-pw//2,y-ph,pw,ph))
    pygame.draw.rect(screen,(255,0,0),(x-sw//2,y-ph-sh,sw,sh))


# ============================================================
#   ROAD + BACKGROUND
# ============================================================
def draw_road():
    mid = TRACK_WIDTH//2
    horizon = 40
    TOP_W = 80
    BOT_W = 700

    screen.fill(SKY_BLUE)
    draw_clouds()

    # grass
    pygame.draw.rect(screen, GREEN, (0, horizon, TRACK_WIDTH, TRACK_HEIGHT-horizon))

    # road body
    pygame.draw.polygon(screen, GRAY, [
        (mid - TOP_W//2, horizon),
        (mid + TOP_W//2, horizon),
        (mid + BOT_W//2, TRACK_HEIGHT),
        (mid - BOT_W//2, TRACK_HEIGHT)
    ])

    # borders
    pygame.draw.line(screen, WHITE, (mid-TOP_W//2,horizon),(mid-BOT_W//2,TRACK_HEIGHT),4)
    pygame.draw.line(screen, WHITE, (mid+TOP_W//2,horizon),(mid+BOT_W//2,TRACK_HEIGHT),4)

    # dashed line
    for i in range(25):
        p = i/25
        y = horizon + p*(TRACK_HEIGHT-horizon)
        if i % 2 == 0:
            pygame.draw.line(screen, WHITE, (mid, y), (mid, y+6), 4)


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
            if car.speed < 45: car.accelerate()
            else: car.brake()

        elif self.state == "OVERTAKE":
            car.accelerate()
            if self.target_lane > car.lane_offset: car.lane_offset += 4
            else: car.lane_offset -= 4
            self.cooldown = 50

        elif self.state == "RETURN":
            if self.target_lane > car.lane_offset: car.lane_offset += 4
            else: car.lane_offset -= 4


# ============================================================
#   PLAYER NAME + START COUNTDOWN
# ============================================================
def get_player_name():
    font = pygame.font.SysFont(None, 48)
    name = ""
    while True:
        screen.fill(WHITE)
        txt = font.render(f"Enter Your Name: {name}", True, BLACK)
        screen.blit(txt,(100,150))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name:
                    return name
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += e.unicode


def start_countdown():
    font = pygame.font.SysFont(None, 100)
    for n in ["3","2","1","GO!"]:
        screen.fill(WHITE)
        t = font.render(n, True, (200,0,0))
        r = t.get_rect(center=(TRACK_WIDTH//2, TRACK_HEIGHT//2))
        screen.blit(t,r)
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

controllers = [
    AIController(LANES[0]),
    AIController(LANES[2])
]

all_cars = [player, ai1, ai2]

player_img = create_3d_car((255,255,0))
ai_imgs = [create_3d_car((200,0,0)), create_3d_car((0,0,255))]

font = pygame.font.SysFont(None, 24)

start_countdown()


# ============================================================
#   MAIN LOOP
# ============================================================
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # Player input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.accelerate()
    if keys[pygame.K_s]: player.brake()
    if keys[pygame.K_a]: player.lane_offset -= 4
    if keys[pygame.K_d]: player.lane_offset += 4
    player.lane_offset = max(LANES[0], min(LANES[2], player.lane_offset))

    player.move()

    # AI
    for ctrl, ai in zip(controllers, [ai1, ai2]):
        ctrl.update(ai, all_cars)
        ai.move()

    # Obstacles
    for car in all_cars:
        for obs in OBSTACLES:
            if abs(car.position - obs) < 5:
                car.brake()

    # Draw world
    draw_road()
    # Draw 3D trees based on distance (static)
    TREE_COLOR = (34, 139, 34)  # dark green foliage
    TRUNK_COLOR = (139, 69, 19)  # brown trunk

    for x, dist in TREE_POSITIONS:
        # Convert distance to y position (perspective)
        y = TRACK_HEIGHT - (dist / TRACK_LENGTH) * (TRACK_HEIGHT - horizon)

        # Scale trees with perspective
        scale = 1.0 - 0.7 * (dist / TRACK_LENGTH)
        if scale < 0.2: scale = 0.2

        trunk_w = int(5 * scale)
        trunk_h = int(20 * scale)
        foliage_h = int(40 * scale)
        foliage_w = int(25 * scale)

        # Draw trunk (rectangle)
        pygame.draw.rect(screen, TRUNK_COLOR, (x - trunk_w // 2, y, trunk_w, trunk_h))

        # Draw 3D foliage (cone-shaped polygon)
        pygame.draw.polygon(screen, TREE_COLOR, [
            (x, y - foliage_h),  # top of the cone
            (x - foliage_w // 2, y),  # bottom left
            (x + foliage_w // 2, y)  # bottom right
        ])

        # Optional: Add a darker inner layer for 3D shading
        pygame.draw.polygon(screen, (0, 100, 0), [
            (x, y - int(foliage_h * 0.8)),
            (x - int(foliage_w * 0.3), y),
            (x + int(foliage_w * 0.3), y)
        ])

    # Draw cars
    # Draw cars
    for car, img in [(player, player_img), (ai1, ai_imgs[0]), (ai2, ai_imgs[1])]:
        dist = car.position
        if dist > TRACK_LENGTH:
            dist = TRACK_LENGTH

        x, y, s = project_to_screen(car.lane_offset, dist)
        w, h = img.get_size()
        scaled = pygame.transform.scale(img, (int(w * s), int(h * s)))
        rect = scaled.get_rect(center=(x, y))
        screen.blit(scaled, rect)

    # HUD
    screen.blit(font.render(
        f"{player.name} Lap {player.telemetry.lap_number}/{TOTAL_LAPS} Speed {int(player.speed)}",
        True, BLACK), (10,10))
    screen.blit(font.render(
        f"AI_1 Speed {int(ai1.speed)}",
        True, BLACK), (10,30))
    screen.blit(font.render(
        f"AI_2 Speed {int(ai2.speed)}",
        True, BLACK), (10,50))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
