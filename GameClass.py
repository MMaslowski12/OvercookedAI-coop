import pygame
from Board import Board
from map_generator import generate_map, generate_test_map
import logging
import tensorflow as tf
import numpy as np
import time
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
class Batch():
    def __init__(self):
        self.states = []
        self.masks = []

class ParallelGame():
    def __init__(self, num_boards=1, misha_playing=True, learning=True, tick_length=999999999, models=[None, None], debug=False, display=True, map_generator=generate_map):
        self.num_boards = num_boards
        self.tick_length = tick_length
        self.map_generator = map_generator
        self.Boards = [Board(map_generator, models=models) for _ in range(num_boards)]
        self.misha_playing = misha_playing
        self.learning = learning
        self.Misha1 = models[0]
        self.Misha2 = models[1]
        self.debug = debug
        self.display = display
        self.action_rate = 8
        self.FPS = 60
        self.tick = 0
        
        if display:
            pygame.init()
            self.clock = pygame.time.Clock()

    def _get_new_actions(self):
        for board in self.Boards:
            board.draw()
        if not self.misha_playing:
            keys = pygame.key.get_pressed()
            for board in self.Boards:
                board.keys_for_player1 = keys
                board.keys_for_player2 = keys
                
            return
            
        Batch1 = Batch()
        Batch2 = Batch()
        
        for board in self.Boards:
            board.add_update_to_batch(Batch1, Batch2)
        
        model_idxs = [self.Misha1.get_qs_and_idxs(Batch1.states, Batch1.masks, batch_size=len(self.Boards), random_exploration=self.learning)[1],
                      self.Misha2.get_qs_and_idxs(Batch2.states, Batch2.masks, batch_size=len(self.Boards), random_exploration=self.learning)[1]]
        
        for i in range(len(self.Boards)):
            self.Boards[i].update_keys(idxs_for_player1=model_idxs[0][i], idxs_for_player2=model_idxs[1][i])
            if self.learning:
                self.Boards[i].Player1.remember_state_and_action(Batch1.states[i], model_idxs[0][i])
                self.Boards[i].Player2.remember_state_and_action(Batch2.states[i], model_idxs[1][i])

    def _update_experiences(self):
        if not self.learning:
            return
            
        for board in self.Boards:
            board.add_experience_to_batch()
            
        self.Misha1.add_batch_to_memory()
        self.Misha2.add_batch_to_memory()

    def _display(self):
        # Create font object if not already created
        if not hasattr(self, 'font'):
            self.font = pygame.font.Font(None, 36)
        
        # Get the first (and only) board for display when num_boards = 1
        board = self.Boards[0]
        
        # Render score text
        score_text = f"Score: {board.get_rewards():.1f}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))                    
        # Position in top-left corner with small padding
        board.screen.blit(score_surface, (10, 10))
        
        pygame.display.flip()

    def _scrutinize_boards(self):
        if not self.learning:
            return
        
        for i, board in enumerate(self.Boards):
            rewards = board.get_rewards()
            if self.last_rewards[i] == rewards:
                #Reset the board
                self.Boards[i] = Board(self.map_generator, models=self.models)
                
            self.last_rewards[i] = rewards
    
    def run(self):
        running = True
        start_time = time.time()
        self.last_rewards = [board.get_rewards() for board in self.Boards]
        
        while running:
            if self.display:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                
                self._display()
                self.clock.tick(self.FPS)   
            
            update_actions = self.tick % self.action_rate == 0
            if update_actions:
                self._get_new_actions()
                            
            for board in self.Boards:
                board.update(update_display = not self.learning)
            
            if self.learning:  # Only scrutinize boards when bots are playing
                if update_actions:
                    self._update_experiences()
            
                # if (self.tick + 1) % (10*60) == 0:  # If the Game is stuck for 10 seconds, terminate it
                #     self._scrutinize_boards()    <- Leave this be for now (if you implement this, be ready to deal with future states not getting tangled up -- maybe they dont by default?)           
                                
            if (self.tick + 1 >= self.tick_length):
                self.Boards[0].game_over()
                if self.learning:
                    running = False
            
            self.tick += 1
        
        if self.display:
            pygame.display.quit()
            pygame.quit()

class Game(ParallelGame):
    def __init__(self, misha_playing=True, learning=True, tick_length=999999999, models=[None, None], debug=False, display=True, map_generator=generate_map):
        super().__init__(num_boards=1, misha_playing=misha_playing, learning=learning, tick_length=tick_length, 
                        models=models, debug=debug, display=display, map_generator=map_generator)