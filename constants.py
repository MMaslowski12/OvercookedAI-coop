
import pygame
import os

SIZE = 32
original_dir = os.getcwd()
os.chdir('Graphics')

FLOOR_GRAPHIC = pygame.image.load('floor.png')
WALL_GRAPHIC = pygame.image.load('wall.png')
PLAYER1_GRAPHIC = pygame.image.load('player1.png')
PLAYER2_GRAPHIC = pygame.image.load('player2.png')
FISH_ICON = pygame.image.load('fish.png')
FISH_PLAIN = pygame.image.load('Plain_fish.png')
FISH_CHOPPED = pygame.image.load("Chopped_fish.png")
FISH_CHOPPED_ICON = pygame.image.load("Chopped_fish_icon.png")

POTATO_ICON = pygame.image.load('potato.png')
POTATO_PLAIN = pygame.image.load('Plain_potato.png')
POTATO_CHOPPED = pygame.image.load("Chopped_potato.png")
POTATO_CHOPPED_ICON = pygame.image.load("Chopped_potato_icon.png")

PLATE_ICON = pygame.image.load("Plate_icon.png")
PLATE_PLAIN = pygame.image.load("Plate_plain.png")

FISH_CRATE_ICON = pygame.image.load('FishCrate.png')
POTATO_CRATE_ICON = pygame.image.load('PotatoCrate.png')
PLATE_CRATE = pygame.image.load("PlateCrate.png")

COUNTERTOP_ICON = pygame.image.load('Countertop.png')
CB_ICON = pygame.image.load("CBoard.png")
CB_KNIFELESS_ICON = pygame.image.load("CB_knifeless.png")
CB_R_ICON = pygame.image.load("CBoard_rotated.png")
CB_R_KNIFELESS_ICON = pygame.image.load("CB_knifeless_rotated.png")

FRYER_ICON = pygame.image.load("Fryer.png")
FRYER_R_ICON = pygame.image.load("Fryer_rotated.png")

WAITER_POINT = pygame.image.load('CBelt.png')
TRASH_CAN = pygame.image.load("Trash_Can.png")

POTATO_FRIED = pygame.transform.scale(pygame.image.load("fried_potato.png"), (32, 32))
POTATO_FRIED_ICON = pygame.transform.scale(pygame.image.load("fried_potato_icon.png"), (32, 32))

FISH_FRIED = pygame.transform.scale(pygame.image.load("fried_fish.png"), (32, 32))
FISH_FRIED_ICON = pygame.transform.scale(pygame.image.load("fried_fish_icon.png"), (32, 32))

PLAYER_SPEED = 4

FISH_GRAPHICS = {
    "icon": FISH_ICON,
    "plain": FISH_PLAIN,
    "chopped": FISH_CHOPPED,
    "chopped_icon": FISH_CHOPPED_ICON,
    "plated_icon": pygame.transform.scale(FISH_FRIED_ICON, (16, 16)),
    "fried": FISH_FRIED,
    "fried_icon": FISH_FRIED_ICON
}

POTATO_GRAPHICS = {
    "icon": POTATO_ICON,
    "plain": POTATO_PLAIN,
    "chopped": POTATO_CHOPPED,
    "chopped_icon": POTATO_CHOPPED_ICON,
    "plated_icon": pygame.transform.scale(POTATO_FRIED_ICON, (16, 16)),
    "fried": POTATO_FRIED,
    "fried_icon": POTATO_FRIED_ICON
}

PLATE_GRAPHICS = {
    "icon": PLATE_ICON,
    "plain": PLATE_PLAIN,
    "chopped": None,
    "chopped_icon": None,
    "plated_icon": None,
    "fried": None,
    "fried_icon": None
}


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

player1_controls = {
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "ACTION": pygame.K_e
}

player2_controls = {
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "ACTION": pygame.K_SPACE
}

os.chdir(original_dir)

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

ROWS = 12
COLS = 18
START_X, START_Y = (80, 60)
END_X, END_Y = (START_X + COLS*SIZE, START_Y + ROWS*SIZE)
