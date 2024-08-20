import pygame
import numpy as np

class ResourceGroup(pygame.sprite.Group):
    #Overriding draw because of a specific nature of resources being drawn
    def draw(self, surface):
        for sprite in self.sprites():
            sprite.determine_position()
        super().draw(surface)


from Objects import CounterTop
import math

Resources = ResourceGroup()
class Resource(pygame.sprite.Sprite):
    def __init__(self, graphics, place):
        self.icon = graphics["icon"]
        self.plain_graphic = graphics["plain"]
        self.chopped_graphic = graphics["chopped"]
        self.chopped_icon = graphics["chopped_icon"]
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
        from Player import Player
        if(isinstance(self.place, Player)):
            player = self.place
            self.position = (player.rect.center[0] + 20, player.rect.center[1] - 20)
            self.image = self.icon
            if(self.chopped):
                self.image = self.chopped_icon
            self.rect = self.image.get_rect(center = self.position)
            
        if(isinstance(self.place, CounterTop)):
            table = self.place
            self.position = table.rect.center
            self.image = self.plain_graphic
            if(self.chopped):
                self.image = self.chopped_graphic
            self.rect = self.image.get_rect(center = self.position)
        
        elif(isinstance(self.place, Plate)):
            pass #Its position is determined when the position of the place is determined - see below:
        
        #Displaying subicons of ingredients in a dish
        elif(isinstance(self, Plate) and len(self.dish) > 0):
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
        self.dish_dict = {Fish: 0, Potato: 0}
    
    def add_ingredient(self, ingredient):
        self.dish.append(ingredient)
        ingredient.place = self
        if isinstance(ingredient, Fish):
            self.dish_dict[Fish] += 1
            
        elif isinstance(ingredient, Potato):
            self.dish_dict[Potato] += 1
            
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
        

class Menu():
    def __init__(self):
        self.queue = []
        self.max_dishes = 5
        self.frequency = 15 #Once every X seconds on average, there will be a new dish
        self.game_score = 0
    
    def update(self):
        #Add a dish 
        #The number of dishes should be capped
        if(len(self.queue) < self.max_dishes):
            decider = random.random()
            probability = self.frequency/1000*60
            if (decider < probability):
                self.generate_new_dish()

        for i in range (len(self.queue)):
            self.queue[i].order_in_queue = i
            self.queue[i].update()
            
            
    def generate_new_dish(self, prob_chips = 0.5):
        decider = random.random()
        if(decider < prob_chips):
            #Add fish and chips
            self.queue.append(Dish("Fish and Chips", [Fish, Potato], {Fish: 1, Potato: 1}, 100, len(self.queue)))
            
        else:
            #Add just fish
            self.queue.append(Dish("Fish", [Fish], {Fish: 1, Potato: 0}, 50, len(self.queue)))
            
    def serve_dish(self, plate):
        for i in range (len(self.queue)):
            order = self.queue[i]
            if (order.ingredients_dict[Fish] == plate.dish_dict[Fish]) and (order.ingredients_dict[Potato] == plate.dish_dict[Potato]):
                self.game_score += order.score
                self.queue.pop(i)
                return True
            
        return False
    
    def get_statecipa(self):
        '''
        Returns the state of the menu. 10 binary values. 2*ith value corresponds to whether the ith dish contains fish, and the 2*i + 1th value corresponds to whether the ith dish contains potatoes 
        '''
        
        state = np.zeros((5, 2)) 
        
        for i in range(len(Menu.queue)):  
            dish = Menu.queue[i]
            
            if dish.name == "Fish and Chips":
                state[i, 0] = 1
                state[i, 1] = 1  #Both fish and potatoes
                
            else:
                state[i, 0] = 1  #Fish only

        return state.flatten()  #Flatten the array from 2D to 1D