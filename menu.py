import random
import pygame
from foods import Fish, Potato
from constants import START_X, START_Y, END_X, WHITE

class Dish(pygame.sprite.Sprite):
    def __init__(self, name, ingredients, ingredients_dict, score, order):
        """Initialize a Dish with its name, required ingredients, corresponding quantities, score, and order position.
        
        Parameters:
            name (str): The name of the dish.
            ingredients (list): List of ingredient classes required for the dish.
            ingredients_dict (dict): Dictionary mapping ingredient names to required counts.
            score (int): The score awarded for serving the dish correctly.
            order (int): The order of the dish in the queue.
        """
        super().__init__()
        self.name = name
        self.ingredients = ingredients
        self.ingredients_dict = ingredients_dict
        self.score = score
        self.order_in_queue = order

import random
class MenuClass():
    def __init__(self):
        """Initialize the game menu, including dish queue, score, and dish generation parameters."""
        self.queue = []
        self.max_dishes = 5
        self.frequency = 15 #Once every X seconds on average, there will be a new dish
        self.game_score = 0
        
        self.font = pygame.font.SysFont("Comic Sans MS", 10)
        self.generate_new_dish()
        self.width = 75
        self.height = 50
    
    def update(self):
        """Update the menu by potentially adding new dishes and updating dish order.
        
        If the dish queue has fewer than max_dishes, a new dish may be added based on a probability derived from frequency.
        Then, update each dish's order index and call its update method.
        """
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
        """Generate a new dish and add it to the queue.
        
        Parameters:
            prob_chips (float): The probability of generating a dish with both fish and chips. Defaults to 0.5.
        """
        decider = random.random()
        if(decider < prob_chips):
            #Add fish and chips
            self.queue.append(Dish("Fish and Chips", [Fish, Potato], {"Fish": 1, "Potato": 1}, 1000, len(self.queue)))
            
        else:
            #Add just fish
            self.queue.append(Dish("Fish", [Fish], {"Fish": 1, "Potato": 0}, 500, len(self.queue)))
            
    def serve_dish(self, plate):
        """Serve a dish using the provided plate if its ingredients match a dish in the queue.
        
        The dish is removed from the queue and the game score is updated accordingly.
        
        Parameters:
            plate: The plate object containing prepared ingredients.
        
        Returns:
            bool: True if a dish was successfully served, otherwise False.
        """
        for i in range (len(self.queue)):
            order = self.queue[i]
            if (order.ingredients_dict["Fish"] == plate.dish_dict["Fish"]) and (order.ingredients_dict["Potato"] == plate.dish_dict["Potato"]):
                self.game_score += order.score
                self.queue.pop(i)
                return True
            
        return False
    
    def draw(self, screen):
        """Draw the menu on the given screen.
        
        Draws a strip representing the background for the dish queue and renders each dish's name and score.
        
        Parameters:
            screen: The pygame surface where the menu will be drawn.
        """
        #Draw a strip:
        strip_left = START_X
        strip_top = START_Y - self.height
        strip_right = END_X
        strip_bottom = START_Y
        gap = 50
        #fill out with background -- a wooden table
        
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
    
Menu = MenuClass()