import pygame
from .Board import Board
from .map_generator import generate_test_map
import time

class Game():
    def __init__(self, tick_length=999999999, debug=False, map_generator=generate_test_map, agents=[None, None]):
        self.tick_length = tick_length
        self.map_generator = map_generator
        self.Board = Board(map_generator, models=agents)
        self.debug = debug
        self.action_rate = 10
        self.FPS = 120
        self.tick = 0
        self.agents = agents
        self.agents[0].set_params(board=self.Board, player=self.Board.Player1)
        self.agents[1].set_params(board=self.Board, player=self.Board.Player2)
        
        pygame.init()
        self.clock = pygame.time.Clock()
    
    def _get_new_actions(self):
        keys1 = self.agents[0].action()
        keys2 = self.agents[1].action()

        return [keys1, keys2]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            
            self.clock.tick(self.FPS)   
            self.Board.display()
            
            update_actions = self.tick % self.action_rate == 0
            if update_actions:
                self.actions = self._get_new_actions()
            
            self.Board.update(actions=self.actions)          
                                
            if (self.tick + 1 >= self.tick_length):
                self.Board.game_over()
            
            self.tick += 1

        pygame.display.quit()
        pygame.quit()
