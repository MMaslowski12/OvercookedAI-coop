from Foods import Fish, Potato, Plate, MenuClass, ResourceGroup
from Objects import Fryer, CBoard, Floor
from Player import Player1, Player2
import numpy as np
import pygame
import tensorflow as tf

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
        
        self.Player1 = Player1(coords2px(player1_coords[1], player1_coords[0]), self, models[0], misha_playing=models[0] is not None)
        self.Players.add(self.Player1)
        self.Player2 = Player2(coords2px(player2_coords[1], player2_coords[0]), self, models[1], misha_playing=models[1] is not None)
        self.Players.add(self.Player2)

        
    def draw(self):
        self.screen.fill((255, 255, 255)) 
        self.StaticObjects.draw(self.screen)
        self.Players.draw(self.screen)
        self.Menu.draw(self.screen, self.corner_coordinates)
        self.Resources.draw(self.screen)
        for interactable in self.Interactables:
            interactable.draw_progress_bar(self.screen)
        
        if self.is_game_over:
            self._draw_game_over()
            #Game finished; display a large "GAME OVER" sign over a frozen frame
    
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
    
    def update(self, update_actions=False):
        if not self.is_game_over:
            self.Interactables.update()
            self.Players.update(update_actions=update_actions, state=None if not update_actions else self.get_state()) #Giving the state here to avoid getting the state multiple times. Only give when update is needed
            self.Menu.update()
            self.draw()
            #Players.push_experience_to_buffer()
            #Either get the agents here -> ugly, but it works
            #Or draw it immediately? And redraw the board multiple times
        
        else:
            self._draw_game_over()
    
    def _get_visual_data(self):
        visual_data = pygame.surfarray.array3d(self.screen)
        visual_data = np.transpose(visual_data, (1, 0, 2)) #Change from width, height, color channel to height, width, color channel
        start_x, start_y, end_x, end_y = self.corner_coordinates
        
        visual_data = visual_data[start_y - self.Menu.height: end_y, start_x:end_x]
        visual_data = visual_data / 255. #Normalize pixels from 0 to 1 for easier training
        visual_data = np.expand_dims(visual_data, axis=0)
        
        visual_data_tensor = tf.convert_to_tensor(visual_data, dtype=tf.float32)
        
        new_size = (108, 144)
        return tf.image.resize(visual_data_tensor, new_size, method='bilinear')
    
    def _get_numerical_data(self):
        numerical_data = self.Menu.get_state()
        for Player in self.Players:
            numerical_data.extend(Player.get_state())
            
        return tf.convert_to_tensor([numerical_data]) #Add a batch dimension

    
    def get_state(self):
        '''
        Returns the list of:
        - visual_data - normalized pixel values of the screen
        - numerical_data, containing in respective order:
            - the state of the Menu (see: Menu.get_state())
            - the state of Player 1's and Player 2's hands (see: Player.get_state())
        
        '''
        
        visual_data = self._get_visual_data()
        numerical_data = self._get_numerical_data()
        
        return [visual_data, numerical_data]
    
    
    def _get_ingredient_rewards(self, ingredient, raw_coeff, prep_coeff):
        reward = raw_coeff
        if ingredient.chopped:
            reward += prep_coeff
        
        if ingredient.fried:
            reward += prep_coeff
            
        if (isinstance(ingredient.place, Fryer) and not ingredient.fried) or (isinstance(ingredient.place, CBoard) and not ingredient.chopped):
            reward += 0.25 * prep_coeff #25% from just being there
            reward += 0.75 * prep_coeff * min(ingredient.progress, 100)/100
            
        return reward
        

    def get_rewards(self):
        '''
        Computes the total amount of rewards for the current game state. 
        Rewards = game score * 10
        Additionally:
        Raw food needed to finish the menu is worth 50 points, 
        Cut food on the menu - 150 points 
        Fried food on the menu - 250 points
        Plate - 500 points
        '''
        
        
        raw_coeff = 50
        prep_coeff = 150
        plate_coeff = 50
        
        '''
        REMEMBER: THERE IS ALSO A PENALTY FOR NOT MOVING WHICH IS HACKED IN THE PLAYER CLASS.
        UNMOVED PENALTY = 10    
        '''
        
        rewards = self.Menu.game_score*10
        
        fish_points = []
        potato_points = []
        plate_points = []
        
        foods = []
        for Interactable in self.Interactables:
            if(Interactable.resource != None):
                foods.append(Interactable.resource) 
        
        for Player in self.Players:
            if(Player.hands != None):
                foods.append(Player.hands)
        
        for food in foods:
            if isinstance(food, Plate):
                plate_points.append(plate_coeff)
                for ingredient in food.dish:
                    reward = self._get_ingredient_rewards(ingredient, raw_coeff, prep_coeff)
                    if isinstance(ingredient, Fish):
                        fish_points.append(reward)
                    
                    if isinstance(ingredient, Potato):
                        potato_points.append(reward)
            
            else:
                reward = self._get_ingredient_rewards(food, raw_coeff, prep_coeff)
                if isinstance(food, Fish):
                    fish_points.append(reward)
                
                if isinstance(food, Potato):
                    potato_points.append(reward)
                    
        fish_on_menu = sum([dish.ingredients_dict["Fish"] for dish in self.Menu.queue])
        potato_on_menu = sum([dish.ingredients_dict["Potato"] for dish in self.Menu.queue])
        plate_on_menu = len(self.Menu.queue)
        
        fish_points.sort(reverse = True)
        potato_points.sort(reverse = True)
        plate_points.sort(reverse = True)
            
        rewards += sum(fish_points[:fish_on_menu])
        rewards += sum(potato_points[:potato_on_menu])
        rewards += sum(plate_points[:plate_on_menu])
        
        return float(rewards)