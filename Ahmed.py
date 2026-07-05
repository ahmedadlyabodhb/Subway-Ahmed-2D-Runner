# -*- coding: utf-8 -*-
import pygame
import random
import sys
import json
import os

pygame.init()
W, H = 400, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Subway Ahmed - Pygame")
clock = pygame.time.Clock()

# Neon Colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 25)
YELLOW = (255, 215, 0)
GRAY = (100, 100, 100)
BLUE = (0, 200, 255)
RED = (255, 50, 50)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)

LANE_W = W // 3
PLAYER_SIZE = 42
SPEED = 7

# Save System
SAVE = "save_pygame.json"
if os.path.exists(SAVE):
    try:
        with open(SAVE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"coins": 0, "high": 0, "owned": ["Ahmed"], "char": "Ahmed"}
else:
    data = {"coins": 0, "high": 0, "owned": ["Ahmed"], "char": "Ahmed"}

coins = data.get("coins", 0)
high = data.get("high", 0)
current_char = data.get("char", "Ahmed")

chars = {
    "Ahmed": {"price": 0, "color": BLUE, "label": "[Normal]"},
    "Ninja": {"price": 400, "color": BLACK, "label": "[Ninja]"},
    "Fire": {"price": 900, "color": RED, "label": "[Fire]"},
    "Ghost": {"price": 2000, "color": PURPLE, "label": "[Ghost]"}
}

# Fonts
font = pygame.font.SysFont("Arial", 18, bold=True)
big = pygame.font.SysFont("Arial", 36, bold=True)

def save_game():
    data["coins"] = coins
    data["high"] = max(high, int(score))
    data["char"] = current_char
    with open(SAVE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

class Player:
    def __init__(self):
        self.lane = 1
        self.x = LANE_W * self.lane + LANE_W//2 - PLAYER_SIZE//2
        self.y = H - 160
        self.tx = self.x
        self.jump = False
        self.slide = False
        self.vy = 0
        self.st = 0

    def mv(self, d):
        if not self.jump and not self.slide:
            if d == "L" and self.lane > 0: self.lane -= 1
            if d == "R" and self.lane < 2: self.lane += 1
            self.tx = LANE_W * self.lane + LANE_W//2 - PLAYER_SIZE//2

    def jp(self):
        if not self.jump:
            self.jump = True
            self.vy = -18

    def sl(self):
        if not self.jump and not self.slide:
            self.slide = True
            self.st = 28

    def update(self):
        if self.x < self.tx: self.x += 14
        if self.x > self.tx: self.x -= 14
        if self.jump:
            self.y += self.vy
            self.vy += 1
            if self.y >= H - 160:
                self.y = H - 160
                self.jump = False
        if self.slide:
            self.st -= 1
            if self.st <= 0:
                self.slide = False

    def draw(self):
        c = chars[current_char]["color"]
        h = PLAYER_SIZE//2 if self.slide else PLAYER_SIZE
        y = self.y + PLAYER_SIZE//2 if self.slide else self.y
        pygame.draw.rect(screen, c, (self.x, y, PLAYER_SIZE, h), border_radius=10)
        pygame.draw.rect(screen, WHITE, (self.x, y, PLAYER_SIZE, h), 3, border_radius=10)

class Obs:
    def __init__(self):
        self.lane = random.randint(0, 2)
        self.type = random.choice(["box", "bar", "train"])
        self.x = LANE_W * self.lane + LANE_W//2 - 32
        self.y = -90
        self.w = 64
        self.h = 66 if self.type == "box" else 24 if self.type == "bar" else 72

    def up(self, s):
        self.y += s

    def draw(self):
        col = RED if self.type == "box" else PURPLE if self.type == "bar" else ORANGE
        pygame.draw.rect(screen, col, (self.x, self.y, self.w, self.h), border_radius=7)

class Coin:
    def __init__(self):
        self.lane = random.randint(0, 2)
        self.x = LANE_W * self.lane + LANE_W//2
        self.y = -35
        self.r = 16

    def up(self, s):
        self.y += s

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.r)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.r, 3)

def draw_bg(s):
    screen.fill((25, 25, 45))
    for i in range(1, 3):
        x = i * LANE_W
        for y in range(0, H, 60):
            pygame.draw.line(screen, WHITE, (x, (y + int(s * 7)) % H), (x, (y + int(s * 7)) % H + 30), 6)
    pygame.draw.rect(screen, GRAY, (0, H - 100, W, 100))

def txt(t, x, y, c=WHITE, f=font):
    screen.blit(f.render(t, True, c), (x, y))

def shop():
    global current_char, coins
    screen.fill(BLACK)
    txt("SHOP MENU", W//2 - 70, 20, YELLOW, big)
    txt(f"Coins: {coins}", 25, 25, YELLOW)
    txt("Press M to Return Game", 25, H - 45)
    y = 120
    for i, name in enumerate(chars.keys(), 1):
        owned = name in data["owned"]
        status = f"Press {i} to Select" if owned else f"Price: {chars[name]['price']}"
        col = WHITE if owned else YELLOW
        txt(f"{i}. {chars[name]['label']} {name}", 30, y, chars[name]["color"])
        txt(status, 200, y, col)
        pygame.draw.rect(screen, chars[name]["color"], (330, y, 35, 35), border_radius=7)
        y += 80

def over(s):
    screen.fill(BLACK)
    txt("GAME OVER", W//2 - 90, H//2 - 90, RED, big)
    txt(f"Score: {int(s)}", W//2 - 40, H//2 - 20)
    txt(f"High Score: {max(high, int(s))}", W//2 - 60, H//2 + 15, YELLOW)
    txt("R = Restart | S = Shop | ESC = Exit", W//2 - 140, H//2 + 70)

# Game Variables
player = Player()
obs = []
coins_list = []
speed = SPEED
score = 0
timer = 0
state = "play"

running = True
while running:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            save_game()
            running = False
        
        if state == "play" and e.type == pygame.KEYDOWN:
            if e.key in [pygame.K_LEFT, pygame.K_a]: player.mv("L")
            if e.key in [pygame.K_RIGHT, pygame.K_d]: player.mv("R")
            if e.key in [pygame.K_UP, pygame.K_w]: player.jp()
            if e.key in [pygame.K_DOWN, pygame.K_s]: player.sl()
            if e.key == pygame.K_m: state = "shop"
            
        elif state == "over" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                player = Player()
                obs = []
                coins_list = []
                score = 0
                speed = SPEED
                state = "play"
            if e.key == pygame.K_s:
                state = "shop"
            if e.key == pygame.K_ESCAPE:
                save_game()
                running = False
                
        elif state == "shop" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_m:
                state = "play"
            for i, name in enumerate(list(chars.keys()), 1):
                if e.key == getattr(pygame, f"K_{i}"):
                    if name in data["owned"]:
                        current_char = name
                    elif coins >= chars[name]["price"]:
                        coins -= chars[name]["price"]
                        data["owned"].append(name)
                        current_char = name
                        save_game()

    if state == "play":
        player.update()
        draw_bg(speed)
        player.draw()

        timer += 1
        if timer > 23:
            timer = 0
            r = random.random()
            if r < 0.5:
                obs.append(Obs())
            elif r < 0.8:
                coins_list.append(Coin())
            else:
                c1 = Coin()
                c2 = Coin()
                c2.lane = (c1.lane + 1) % 3
                c2.x = LANE_W * c2.lane + LANE_W//2
                coins_list.extend([c1, c2])

        for o in obs[:]:
            o.up(speed)
            o.draw()
            if o.y > H: obs.remove(o)
            if o.type == "box" and not player.jump:
                if abs(player.x - o.x) < 43 and abs(player.y - o.y) < 53:
                    state = "over"
                    save_game()
            if o.type in ["bar", "train"] and not player.slide:
                if abs(player.x - o.x) < 43 and abs(player.y - o.y) < 46:
                    state = "over"
                    save_game()

        for c in coins_list[:]:
            c.up(speed)
            c.draw()
            if c.y > H: coins_list.remove(c)
            if abs(player.x + 21 - c.x) < 32 and abs(player.y + 21 - c.y) < 32:
                coins += 1
                coins_list.remove(c)

        score += 0.2
        speed += 0.004

        txt(f"Score: {int(score)}", 18, 50)
        txt(f"Coins: {coins}", 18, 82, YELLOW)
        txt("UP Jump | DOWN Slide | M Shop", 15, 22)

    elif state == "shop":
        shop()
    elif state == "over":
        over(score)

    pygame.display.flip()

pygame.quit()
sys.exit()
