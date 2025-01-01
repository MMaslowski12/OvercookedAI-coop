import pygame
from Board import Board
from map_generator import generate_map

class Game:
    def __init__(self, misha_playing, tick_length=999999999, agent = None):
        pygame.init()    
        self.Board = Board(generate_map)
        
        self.misha_playing = misha_playing
        self.tick_length = tick_length
        self.clock = pygame.time.Clock()
        
        if misha_playing:
            self.Agent = agent 
        
        self.start_time = pygame.time.get_ticks()
        
    def qs2actions(self, qs):
        p1_values = qs[0:5]
        p1_idx = p1_values.argmax() #Get the action from player 1 that maximizes the q value",
        
        if (p1_idx == 4 and (not self.Board.Player1.action_possible())):
            p1_idx = p1_values[0:4].argmax() #Get the 2nd best action if an action is the best one and isn't possible",
        
        p2_values = qs[5:10]
        p2_idx = p2_values.argmax() #Get the action from player 1 that maximizes the q value\n",
        
        if (p2_idx == 4 and (not self.Board.Player2.action_possible())):
            p2_idx = p2_values[0:4].argmax() #Get the 2nd best action if an action is the best one and isn't possible",
        
        keys = [key for key in dir(pygame) if key.startswith('K_')]
        actions = {getattr(pygame, key): False for key in keys}
        
        actions[list(self.Board.player1_controls.values())[p1_idx]] = True
        actions[list(self.Board.player2_controls.values())[p2_idx]] = True
        
        return [p1_idx, p2_idx], actions
            
    
    def get_actions(self):
        if (self.misha_playing):
            state = self.Board.get_state()
            qs = self.Agent.get_qs(state, random_exploration=self.Agent.learning)    
                
            action_idxs, actions = self.qs2actions(qs)
            update_buffer = self.Agent.learning and (self.tick + 1 < self.tick_length) #The last action has no consequences
            if (update_buffer):
                self.Agent.add_actions_to_memory(state, action_idxs)
        
        else:
            actions = pygame.key.get_pressed()
        
        return actions
    
    def _get_consequences(self):
        rewards = self.Board.get_rewards()
        if(self.tick != 0): 
            self.Agent.add_consequences_to_memory(self.Board.get_state(), rewards - self.former_rewards)
        
        self.former_rewards = self.rewards
        
    
    def run(self):
        running = True
        self.tick = 0
        while running:
            if not self.misha_playing or not self.Agent.learning:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    
                pygame.display.flip()
                self.clock.tick(60)   
                
            if (self.tick % 5 == 0):
                #The Consequences
                if self.misha_playing and self.Agent.learning:
                    self._get_consequences()
                
                actions = self.get_actions()
                
            self.Board.update(actions)
                                
            if (self.tick + 1 == self.tick_length):
                self.Board.game_over()
                if self.misha_playing and self.Agent.learning:
                    running = False
            
            self.tick += 1
                
        pygame.display.quit()
        pygame.quit()
            
    
    