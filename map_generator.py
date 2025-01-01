from Objects import CBoard, Fryer, CBelt, TrashCan, Floor, Wall, CounterTop, FishCrate, PotatoCrate, PlateCrate
from Player import Player1, Player2


def generate_map():
    SIZE = 32
    ROWS = 12
    COLS = 18
    screen_width = 800
    screen_height = 600
    
    START_X, START_Y = (int(screen_width // 2 - 1/2*SIZE*COLS), int(screen_height // 2 - 1/2*SIZE*ROWS))
    END_X, END_Y = START_X + SIZE*COLS, START_Y + SIZE*COLS

    '''
    0: Floor
    1: Wall
    2: Countertop
    3: Fish
    4: Potato
    5: Plate
    6: CBoard
    7: Fryer
    8: CBelt
    9: TrashCan
    '''
    
    obj_types = [Floor, 
                Wall, 
                CounterTop,
                FishCrate,
                PotatoCrate,
                PlateCrate,
                CBoard,
                Fryer,
                CBelt,
                TrashCan]
    
    def idx2obj(x):
        return obj_types[x]
    
    floor_plan_matrix = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 1, 1, 1],
                         [1, 2, 2, 2, 2, 7, 6, 3, 2, 2, 2, 1, 5, 8, 8, 9, 2, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 4, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 6, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 7, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
                         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    '''
    floor_plan_matrix = [([0]*COLS) for _ in range(ROWS)]
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


    for i in range (WALL_LENGTH):
        floor_plan_matrix[i][WALL_COLUMN] = 1

    fish_x, fish_y = (8, 1)
    floor_plan_matrix[fish_y][fish_x] = 3

    potato_x, potato_y = (COLS-2, 5)
    floor_plan_matrix[potato_y][potato_x] = 4

    plate_x, plate_y = (WALL_COLUMN+1, 1)
    floor_plan_matrix[plate_y][plate_x] = 5

    CB1_x, CB1_y = fish_x-1, fish_y
    floor_plan_matrix[CB1_y][CB1_x] = 6

    CB2_x, CB2_y = potato_x, potato_y+1
    floor_plan_matrix[CB2_y][CB2_x] = 6

    Fryer1_x, Fryer1_y = CB1_x-1, CB1_y
    floor_plan_matrix[Fryer1_y][Fryer1_x] = 7

    Fryer2_x, Fryer2_y = CB2_x, CB2_y+1
    floor_plan_matrix[Fryer2_y][Fryer2_x] = 7

    CBelt1_x, CBelt1_y = plate_x+1, plate_y
    floor_plan_matrix[CBelt1_y][CBelt1_x] = 8

    CBelt2_x, CBelt2_y = CBelt1_x+1, CBelt1_y
    floor_plan_matrix[CBelt2_y][CBelt2_x] = 8

    CBelt3_x, CBelt3_y = CBelt1_x, CBelt1_y-1
    floor_plan_matrix[CBelt3_y][CBelt3_x] = 8

    CBelt4_x, CBelt4_y = CBelt1_x+1, CBelt1_y-1
    floor_plan_matrix[CBelt4_y][CBelt4_x] = 8

    Trash_x, Trash_y = CBelt2_x+1, CBelt2_y
    floor_plan_matrix[Trash_y][Trash_x] = 9
    
    Player1_x, Player1_y = fish_x, fish_y + 1
    floor_plan_matrix[Player1_y][Player1_x] = 10
    
    Player2_x, Player2_y = potato_x, potato_y
    floor_plan_matrix[Player2_y][Player2_x] = 11
    
    '''
    
    def coords2px(x, y):
        return START_X + SIZE/2 + x*SIZE, START_Y+SIZE/2 + y*SIZE
    
    player1_coords = (2, 7)
    player1_setup = (player1_coords, Player1)
    
    player2_coords = (5, 15)
    player2_setup = (player2_coords, Player2)
    
    players = [player1_setup, player2_setup]
    
    return floor_plan_matrix, idx2obj, coords2px, (START_X, START_Y, END_X, END_Y), players

    #Finish dealing with Player actions and interaction methods. Important: double-check placing down on CBoards and Fryers, especially the knife removal thing?
    #Fix up everything with unresolved problems
    #Do basic tests for the Misha part.
    #Test the code by yoursel



 
