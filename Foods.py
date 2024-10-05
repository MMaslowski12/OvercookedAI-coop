import pygame
import numpy as np
from constants import START_X, START_Y, END_X, WHITE
import pygame
pygame.init()

class ResourceGroup(pygame.sprite.Group):
    #Overriding draw because of a specific nature of resources being drawn
    def draw(self, surface):
        for sprite in self.sprites():
            sprite.determine_position()
        super().draw(surface)


import math

Resources = ResourceGroup()
class Resource(pygame.sprite.Sprite):
    def __init__(self, graphics, place):
        self.icon = graphics["icon"]
        self.plain_graphic = graphics["plain"]
        self.chopped_graphic = graphics["chopped"]
        self.chopped_icon = graphics["chopped_icon"]
        self.fried_graphic = graphics["fried"]
        self.fried_icon = graphics["fried_icon"]
        self.plated_icon = graphics["plated_icon"]
        self.chopped = False
        self.fried = False
        self.place = place
        self.position = None
        self.image = None
        self.rect = None
        super().__init__()
        Resources.add(self)
        
        
    def determine_position(self):
        place = self.place.__class__.__name__ #Going around the circular import problem.
        #Displaying subicons of ingredients in a dish
        if(isinstance(self, Plate) and len(self.dish) > 0):
            y_gap = 20
            x_gap = 10
            rows_no = math.ceil(len(self.dish)/2)
            for i in range (len(self.dish)):
                ingredient = self.dish[i]
                ingredient.image = ingredient.plated_icon
                #This many rows
                row = i//2
                y = self.position[1] - rows_no * y_gap + row * y_gap
                x = self.position[0]
                #If it's the left element and is not the last one, it goes to the left. If it is the last one and is the left element, it should stay in the middle
                if ((i % 2 == 0) and (i < len(self.dish) - 1)):
                    x -= x_gap
                
                if (i % 2 == 1):
                    x += x_gap
                
                ingredient.rect = ingredient.image.get_rect(center = (x, y))
        
        if(place == "Player"):
            player = self.place
            self.position = (player.rect.center[0] + 20, player.rect.center[1] - 20)
            self.image = self.icon
            if self.chopped:
                self.image = self.chopped_icon
                
            if self.fried:
                self.image = self.fried_icon
            
            self.rect = self.image.get_rect(center = self.position)
            
        if(place == "CounterTop" or place == "CBoard" or place == "Fryer"):
            table = self.place
            self.position = table.rect.center
            self.image = self.plain_graphic
            if self.chopped:
                self.image = self.chopped_graphic
                
            if self.fried:
                self.image = self.fried_graphic
                
            self.rect = self.image.get_rect(center = self.position)
        
        elif(place == "Plate"):
            pass #Its position is determined when the position of the place is determined - see below:
        

    def chop(self):
        self.chopped = True
        
    def fry(self):
        self.fried = True

from constants import FISH_GRAPHICS, POTATO_GRAPHICS, PLATE_GRAPHICS
class Fish(Resource):
    def __init__(self, place):
        super().__init__(FISH_GRAPHICS, place)

class Potato(Resource):
    def __init__(self, place):
        super().__init__(POTATO_GRAPHICS, place)

class Plate(Resource):
    def __init__(self, place):
        super().__init__(PLATE_GRAPHICS, place)
        self.dish = []
        self.dish_dict = {"Fish": 0, "Potato": 0}
    
    def add_ingredient(self, ingredient):
        self.dish.append(ingredient)
        ingredient.place = self
        if isinstance(ingredient, Fish):
            self.dish_dict["Fish"] += 1
            
        elif isinstance(ingredient, Potato):
            self.dish_dict["Potato"] += 1
            
#Menu is a queue
menu = []
import random
class Dish(pygame.sprite.Sprite):
    def __init__(self, name, ingredients, ingredients_dict, score, order):
        super().__init__()
        self.name = name
        self.ingredients = ingredients
        self.ingredients_dict = ingredients_dict
        self.score = score
        self.order_in_queue = order
        

class MenuClass():
    def __init__(self):
        self.queue = []
        self.max_dishes = 4
        self.frequency = 15 #Once every X seconds on average, there will be a new dish
        self.game_score = 0
        
        self.font = pygame.font.SysFont("Comic Sans MS", 10)
        self.generate_new_dish()
        self.width = 75
        self.height = 50
    
    def update(self):
        #Add a dish 
        #The number of dishes should be capped
        if(len(self.queue) < self.max_dishes):
            decider = random.random()
            probability = 1/60 * 1/self.frequency
            if (decider < probability):
                self.generate_new_dish()

        for i in range (len(self.queue)):
            self.queue[i].order_in_queue = i
            self.queue[i].update()
            
            
    def generate_new_dish(self, prob_chips = 0.5):
        decider = random.random()
        if(decider < prob_chips):
            #Add fish and chips
            self.queue.append(Dish("Fish and Chips", [Fish, Potato], {"Fish": 1, "Potato": 1}, 1000, len(self.queue)))
            
        else:
            #Add just fish
            self.queue.append(Dish("Fish", [Fish], {"Fish": 1, "Potato": 0}, 500, len(self.queue)))
            
    def serve_dish(self, plate):
        for i in range (len(self.queue)):
            order = self.queue[i]
            if (order.ingredients_dict["Fish"] == plate.dish_dict["Fish"]) and (order.ingredients_dict["Potato"] == plate.dish_dict["Potato"]):
                self.game_score += order.score
                self.queue.pop(i)
                return True
            
        return False
    
    def draw(self, screen):
        #Draw a strip:
        strip_left = START_X
        strip_top = START_Y - self.height
        strip_right = END_X
        strip_bottom = START_Y
        gap = 50
        #fill out with background -- a wooden table?
        
        strip_color = (240, 230, 200)  # Light wood color
        pygame.draw.rect(screen, strip_color, (strip_left, strip_top, strip_right - strip_left, strip_bottom - strip_top))
        
        for idx, dish in enumerate(self.queue):
            left_x = strip_left + idx*(self.width + gap)
            top_y = strip_top
            pygame.draw.rect(screen, WHITE, (left_x, top_y, self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (left_x, top_y, self.width, self.height), 2)
            
            dish_name_text = f"{dish.name}"
            name_surface = self.font.render(dish_name_text, True, (0, 0, 0))
            score_text = f"{dish.score} pts"
            score_surface = self.font.render(score_text, True, (0, 0, 0))


            # Blit the text onto the screen
            text_x = left_x + (self.width - name_surface.get_width()) // 2
            name_text_y = top_y + (self.height - name_surface.get_height()) // 2
            score_text_y = name_text_y + name_surface.get_height()
            screen.blit(name_surface, (text_x, name_text_y))
            
            screen.blit(name_surface, (text_x, name_text_y))
            screen.blit(score_surface, (text_x, score_text_y))
            
            
        
    
    def get_state(self):
        '''
        Returns the state of the menu. 10 binary values. 2*ith value corresponds to whether the ith dish contains fish, and the 2*i + 1th value corresponds to whether the ith dish contains potatoes 
        '''
        
        state = np.zeros((5, 2)) 
        
        for i in range(len(self.queue)):  
            dish = self.queue[i]
            
            if dish.name == "Fish and Chips":
                state[i, 0] = 1
                state[i, 1] = 1  #Both fish and potatoes
                
            else:
                state[i, 0] = 1  #Fish only

        return state.flatten()  #Flatten the array from 2D to 1D
    
Menu = MenuClass()