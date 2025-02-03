import pygame
from Board import Board
from map_generator import generate_map
import logging
import tensorflow as tf
import time
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
class Game:
    def __init__(self, misha_playing, learning, tick_length=999999999, models = [None, None],  debug = False, visual_debug = False):
        pygame.init()    
        self.Board = Board(generate_map, models=models)
        self.misha_playing = misha_playing
        self.learning = learning
        self.tick_length = tick_length
        self.clock = pygame.time.Clock()
        self.action_rate = 8
        self.FPS = 60
        self.debug = debug
        self.visual_debug = visual_debug
        self.action_count = 0
            
        self.start_time = pygame.time.get_ticks()
    
    # def _debug_sonda(self):
    #     moves = ["UP", "DOWN", "LEFT", "RIGHT", "ACTION"]
    #     qs = self.Agent.get_qs(self.Board.get_state(), random_exploration=False)
    #     action_idxs, _ = self.qs2actions(qs)
    #     logging.debug(f"Qs: {qs} \n Optimal moves: {moves[action_idxs[0]], moves[action_idxs[1]]}. \n Delta: {(qs[action_idxs[0]] + qs[action_idxs[1]])/(2*sum(qs))} \n /")    
        
    def run(self):
        running = True
        self.tick = 0
        start_time = time.time()
        self.last_rewards = self.Board.get_rewards()
        
        while running:
            if not self.learning or self.visual_debug:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    
                if self.visual_debug:
                    # Create font object if not already created
                    if not hasattr(self, 'font'):
                        self.font = pygame.font.Font(None, 36)
                    
                    # Render score text
                    score_text = f"Score: {self.Board.get_rewards():.1f}"
                    score_surface = self.font.render(score_text, True, (0, 0, 0))                    
                    # Position in top-left corner with small padding
                    self.Board.screen.blit(score_surface, (10, 10))
                    # self.Board.draw_q_value_heatmap(self.Agent, update=self.tick % 600 == 0)
                        
                pygame.display.flip()
                self.clock.tick(self.FPS)   
                
            update_actions = False
            if (self.tick % self.action_rate == 0):
                #Update the actions only once per action_rate. See player's update()
                update_actions = True
                self.action_count += 1
                
            self.Board.update(update_actions=update_actions)
            
            if (self.tick + 1) % (20*60) == 0: #If the Game is stuck for 20 seconds, terminate it
                rewards = self.Board.get_rewards()
                if rewards == self.last_rewards:
                    running = False 
                    
                self.last_rewards = rewards
                                
            if (self.tick + 1 == self.tick_length):
                self.Board.game_over()
                if self.learning:
                    running = False
            
            self.tick += 1
                
        pygame.display.quit()
        pygame.quit()
            
    
    