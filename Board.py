from Objects import ResourceSource, CBoard, Fryer, CBelt, TrashCan, Floor, Floors, Wall, Walls, CounterTop, CounterTops
from constants import COLS, ROWS, SIZE, START_X, START_Y, END_X, END_Y, FISH_CRATE_ICON, POTATO_CRATE_ICON, PLATE_CRATE, CB_R_ICON, FRYER_R_ICON
from Foods import Fish, Potato, Plate

WALL_COLUMN = 11
WALL_LENGTH = 8
floor_plan_matrix = [([0]*COLS) for _ in range(ROWS)]

#0 = FLOOR, 1 = WALL, 2 = COUNTERTOP, 3 = SPECIAL ELEMENT
for i in range (COLS):
    floor_plan_matrix[0][i] = 1
    if(i >  0 and i < COLS-1):
        floor_plan_matrix[1][i] = 2
    floor_plan_matrix[ROWS-1][i] = 1

for i in range (ROWS):
    floor_plan_matrix[i][0] = 1
    floor_plan_matrix[i][COLS-1] = 1
    if(i > 0 and i < ROWS-1):
        floor_plan_matrix[i][COLS-2] = 2


for i in range (8):
    floor_plan_matrix[i][WALL_COLUMN] = 1
    
fish_x, fish_y = (8, 1)
floor_plan_matrix[fish_y][fish_x] = 3
FishCrate = ResourceSource((START_X+SIZE/2 + fish_x*SIZE, START_Y+SIZE/2 + fish_y*SIZE), Fish, FISH_CRATE_ICON)

potato_x, potato_y = (COLS-2, 5)
floor_plan_matrix[potato_y][potato_x] = 3
PotatoCrate = ResourceSource((START_X+SIZE/2 + potato_x*SIZE, START_Y+SIZE/2 + potato_y*SIZE), Potato, POTATO_CRATE_ICON)

plate_x, plate_y = (WALL_COLUMN+1, 1)
floor_plan_matrix[plate_y][plate_x] = 3
PotatoCrate = ResourceSource((START_X+SIZE/2 + plate_x*SIZE, START_Y+SIZE/2 + plate_y*SIZE), Plate, PLATE_CRATE)


CB1_x, CB1_y = fish_x-1, fish_y
floor_plan_matrix[CB1_y][CB1_x] = 3
CBoard1 = CBoard((START_X+SIZE/2 + CB1_x*SIZE, START_Y+SIZE/2 + CB1_y*SIZE))


CB2_x, CB2_y = potato_x, potato_y+1
floor_plan_matrix[CB2_y][CB2_x] = 3
CBoard2 = CBoard((START_X+SIZE/2 + CB2_x*SIZE, START_Y+SIZE/2 + CB2_y*SIZE), None, CB_R_ICON)


Fryer1_x, Fryer1_y = CB1_x-1, CB1_y
floor_plan_matrix[Fryer1_y][Fryer1_x] = 3
Fryer1 = Fryer((START_X+SIZE/2 + Fryer1_x*SIZE, START_Y+SIZE/2 + Fryer1_y*SIZE))

Fryer2_x, Fryer2_y = CB2_x, CB2_y+1
floor_plan_matrix[Fryer2_y][Fryer2_x] = 3
Fryer2 = Fryer((START_X+SIZE/2 + Fryer2_x*SIZE, START_Y+SIZE/2 + Fryer2_y*SIZE), None, FRYER_R_ICON)

CBelt1_x, CBelt1_y = plate_x+1, plate_y
floor_plan_matrix[CBelt1_y][CBelt1_x] = 3
CBelt1 = CBelt((START_X+SIZE/2 + CBelt1_x*SIZE, START_Y+SIZE/2 + CBelt1_y*SIZE))

CBelt2_x, CBelt2_y = CBelt1_x+1, CBelt1_y
floor_plan_matrix[CBelt2_y][CBelt2_x] = 3
CBelt2 = CBelt((START_X+SIZE/2 + CBelt2_x*SIZE, START_Y+SIZE/2 + CBelt2_y*SIZE))

CBelt3_x, CBelt3_y = CBelt1_x, CBelt1_y-1
floor_plan_matrix[CBelt3_y][CBelt3_x] = 3
CBelt3 = CBelt((START_X+SIZE/2 + CBelt3_x*SIZE, START_Y+SIZE/2 + CBelt3_y*SIZE))

CBelt4_x, CBelt4_y = CBelt1_x+1, CBelt1_y-1
floor_plan_matrix[CBelt4_y][CBelt4_x] = 3
CBelt4 = CBelt((START_X+SIZE/2 + CBelt4_x*SIZE, START_Y+SIZE/2 + CBelt4_y*SIZE))


Trash_x, Trash_y = CBelt2_x+1, CBelt2_y
floor_plan_matrix[Trash_y][Trash_x] = 3
Trash = TrashCan((START_X+SIZE/2 + Trash_x*SIZE, START_Y+SIZE/2 + Trash_y*SIZE))

obj_types = [[Floor, Floors], [Wall, Walls], [CounterTop, CounterTops]]
for i in range (ROWS):
    for j in range (COLS):
        if(floor_plan_matrix[i][j] < 3):
            obj_class, obj_sprite = obj_types[floor_plan_matrix[i][j]]
            object = obj_class([START_X+SIZE/2 + j*SIZE, START_Y+SIZE/2 + i*SIZE])
            obj_sprite.add(object)
            

player1_start = (START_X + 7*SIZE, START_Y + 3*SIZE)
player2_start = (END_X - 3*SIZE, START_Y + 7*SIZE)