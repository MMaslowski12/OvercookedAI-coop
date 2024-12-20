from constants import COLS, ROWS
from Board import coords2px

for row in range(1, ROWS):
    for col in range (1, COLS):
        x, y = coords2px(row, col)
        
        
        