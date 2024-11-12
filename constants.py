import pygame
SIZE = 32
ROWS = 12
COLS = 18
screen_width = 800
screen_height = 600
START_X, START_Y = (int(screen_width // 2 - 1/2*SIZE*COLS), int(screen_height // 2 - 1/2*SIZE*ROWS))
END_X, END_Y = (START_X + SIZE*COLS, START_Y + SIZE*ROWS)
screen = pygame.display.set_mode((screen_width, screen_height))


import os
os.chdir('Graphics')



FLOOR_GRAPHIC = pygame.image.load('Floor.png')
WALL_GRAPHIC = pygame.image.load('Wall.png')
PLAYER1_GRAPHIC = pygame.image.load('player1.png')
PLAYER2_GRAPHIC = pygame.image.load('player2.png')
FISH_ICON = pygame.image.load('Fish.png')
FISH_PLAIN = pygame.image.load('Plain_fish.png')
FISH_CHOPPED = pygame.image.load("Chopped_fish.png")
FISH_CHOPPED_ICON = pygame.image.load("Chopped_fish_icon.png")

POTATO_ICON = pygame.image.load('Potato.png')
POTATO_PLAIN = pygame.image.load('Plain_potato.png')
POTATO_CHOPPED = pygame.image.load("Chopped_potato.png")
POTATO_CHOPPED_ICON = pygame.image.load("Chopped_potato_icon.png")

FISH_FRIED = pygame.image.load('fried_fish.png')
FISH_FRIED_ICON = pygame.image.load('fried_fish_icon.png')

POTATO_FRIED = pygame.image.load('fried_potato.png')
POTATO_FRIED_ICON = pygame.image.load('fried_potato_icon.png')

PLATE_ICON = pygame.image.load("Plate_icon.png")
PLATE_PLAIN = pygame.image.load("Plate_plain.png")

resource_graphic = [POTATO_PLAIN, POTATO_CHOPPED, POTATO_FRIED, FISH_PLAIN, FISH_CHOPPED, FISH_FRIED]
resource_icon = [POTATO_ICON, POTATO_CHOPPED_ICON, POTATO_FRIED_ICON, FISH_ICON, FISH_CHOPPED_ICON, FISH_FRIED_ICON]


PLATE_ICON = pygame.transform.scale(PLATE_ICON, (32, 32))
PLATE_PLAIN = pygame.transform.scale(PLATE_PLAIN, (32, 32))
POTATO_ICON = pygame.transform.scale(POTATO_ICON, (32, 32))
POTATO_CHOPPED_ICON = pygame.transform.scale(POTATO_CHOPPED_ICON, (32, 32))
POTATO_FRIED_ICON = pygame.transform.scale(POTATO_FRIED_ICON, (32, 32))
FISH_ICON = pygame.transform.scale(FISH_ICON, (32, 32))
FISH_CHOPPED_ICON = pygame.transform.scale(FISH_CHOPPED_ICON, (32, 32))
FISH_FRIED_ICON = pygame.transform.scale(FISH_FRIED_ICON, (32, 32))
POTATO_PLAIN = pygame.transform.scale(POTATO_PLAIN, (32, 32))
POTATO_CHOPPED = pygame.transform.scale(POTATO_CHOPPED, (32, 32))
POTATO_FRIED = pygame.transform.scale(POTATO_FRIED, (32, 32))
FISH_PLAIN = pygame.transform.scale(FISH_PLAIN, (32, 32))
FISH_CHOPPED = pygame.transform.scale(FISH_CHOPPED, (32, 32))
FISH_FRIED = pygame.transform.scale(FISH_FRIED, (32, 32))

for i in range(len(resource_graphic)):
    resource_graphic[i] = pygame.transform.scale(resource_graphic[i], (32, 32))

# Scale the images in resource_icon list
for i in range(len(resource_icon)):
    resource_icon[i] = pygame.transform.scale(resource_icon[i], (32, 32))

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

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

PLATE_GRAPHICS = {
    "icon": PLATE_ICON,
    "plain": PLATE_PLAIN,
    "chopped": None,
    "chopped_icon": None,
    "fried": None,
    "fried_icon": None,
    "plated_icon": None
}

POTATO_GRAPHICS = {
    "icon": POTATO_ICON,
    "plain": POTATO_PLAIN,
    "chopped": POTATO_CHOPPED,
    "chopped_icon": POTATO_CHOPPED_ICON,
    "fried": POTATO_FRIED,
    "fried_icon": POTATO_FRIED_ICON,
    "plated_icon": pygame.transform.scale(POTATO_FRIED_ICON, (16, 16))
}

FISH_GRAPHICS = {
    "icon": FISH_ICON,
    "plain": FISH_PLAIN,
    "chopped": FISH_CHOPPED,
    "chopped_icon": FISH_CHOPPED_ICON,
    "fried": FISH_FRIED,
    "fried_icon": FISH_FRIED_ICON,
    "plated_icon": pygame.transform.scale(FISH_FRIED_ICON, (16, 16))
}