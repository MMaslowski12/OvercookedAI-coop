from .Foods import Fish, Potato, Plate, MenuClass, ResourceGroup
from .Objects import Fryer, CBoard, Floor
from .Player import Player1, Player2
import numpy as np
import pygame
import tensorflow as tf
import time

class Board:
    def __init__(self, map_generator, models=[None, None]):
        self.screen = pygame.display.set_mode((800, 600))
        self.Menu = MenuClass()
        self.StaticObjects = pygame.sprite.Group()
        self.Interactables = pygame.sprite.Group()
        self.NonPassables = pygame.sprite.Group()
        self.Players = pygame.sprite.Group()
        self.Resources = ResourceGroup()
        self.is_game_over = False
        #Get Interactables, NonPassables and Players, too
        
        floor_plan_matrix, idx2obj, coords2px, self.corner_coordinates, player1_coords, player2_coords = map_generator()
        for i in range (len(floor_plan_matrix)):
            for j in range (len(floor_plan_matrix[0])):     
                obj_class = idx2obj(floor_plan_matrix[i][j])     
                x, y = coords2px(j, i)
                object = obj_class(position=[x, y], board=self) 
                self.StaticObjects.add(object)
                if (object.is_nonpassable()):
                    self.NonPassables.add(object)
                
                if (object.is_interactable()):
                    self.Interactables.add(object)
        
        self.Player1 = Player1(coords2px(player1_coords[1], player1_coords[0]), self, agent=models[0], misha_playing=models[0] is not None)
        self.Players.add(self.Player1)
        self.Player2 = Player2(coords2px(player2_coords[1], player2_coords[0]), self, agent=models[1], misha_playing=models[1] is not None)
        self.Players.add(self.Player2)
        
        self.last_rewards = 0
        self.keys_for_player1 = None
        self.keys_for_player2 = None
        self.draw()

        
    def draw(self):
        self.screen.fill((255, 255, 255)) 
        self.StaticObjects.draw(self.screen)
        self.Players.draw(self.screen)
        self.Menu.draw(self.screen, self.corner_coordinates)
        self.Resources.draw(self.screen)
        self.Player1.Agent.draw_policy_info(self.screen, (0, 0))
        self.Player2.Agent.draw_policy_info(self.screen, (0, 20))

        for interactable in self.Interactables:
            interactable.draw_progress_bar(self.screen)
        
        if self.is_game_over:
            self._draw_game_over()
            #Game finished; display a large "GAME OVER" sign over a frozen frame

    def display(self):
        pygame.display.update()
        pygame.display.flip()
    
    def _draw_game_over(self):
        START_X, START_Y, END_X, END_Y   = self.corner_coordinates
        
        font = pygame.font.SysFont("comicsansms", 100)
        game_over_surface = font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=((START_X+END_X)//2, (START_Y + END_Y)//2))
        
        score_text = f"Final Score: {self.Menu.game_score}"
        score_surface = font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(center=((START_X + END_X) // 2, (START_Y + END_Y) // 2 + 100))
        
        self.screen.blit(game_over_surface, game_over_rect)
        self.screen.blit(score_surface, score_rect)
    
    def game_over(self):
        #SET GAME_OVER AS TRUE, ADD DRAWING GAME_OVER TO SELF.DRAW()
        self.is_game_over = True
    
    def update(self, actions, update_display=True): 
        if not self.is_game_over:
            self.Interactables.update()
            self.Player1.update(actions=actions[0])
            self.Player2.update(actions=actions[1])
            self.Menu.update()
            if update_display:
                self.draw()
        
        else:
            self._draw_game_over()
    
    def get_state(self):
        visual_data = pygame.surfarray.array3d(self.screen)
        visual_data = np.transpose(visual_data, (1, 0, 2)) #Change from width, height, color channel to height, width, color channel
        start_x, start_y, end_x, end_y = self.corner_coordinates
        
        visual_data = visual_data[start_y - self.Menu.height: end_y, start_x:end_x]
        # visual_data = np.expand_dims(visual_data, axis=0)
        
        visual_data_tensor = tf.convert_to_tensor(visual_data, dtype=tf.float32)
        
        return visual_data_tensor