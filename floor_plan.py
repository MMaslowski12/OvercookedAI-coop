from constants import *
floor_plan_matrix = [([0]*COLS) for _ in range(ROWS)]

#0 = FLOOR, 1 = WALL, 2 = COUNTERTOP, 3 = SPECIAL ELEMENT - CRATE, CUTTING BOARD, FRYER; 
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

WALL_COLUMN = 11
WALL_LENGTH = 8
for i in range (8):
    floor_plan_matrix[i][WALL_COLUMN] = 1