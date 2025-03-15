import pygame
import math
from objects import CounterTop
from constants import FISH_GRAPHICS, POTATO_GRAPHICS, PLATE_GRAPHICS

class ResourceGroup(pygame.sprite.Group):
    def draw(self, surface):
        """Draw all resources on the given surface after updating their positions.
        
        For each sprite in the group, update its position using determine_position() before drawing.
        
        Parameters:
            surface: The pygame surface where the resources will be drawn.
        """
        for sprite in self.sprites():
            sprite.determine_position()
        super().draw(surface)

Resources = ResourceGroup()
class Resource(pygame.sprite.Sprite):
    def __init__(self, graphics, place):
        """Initialize a Resource with given graphics and assign its initial place.
        
        Parameters:
            graphics (dict): A dictionary containing various image surfaces for different resource states.
            place: The object where the resource is initially located.
        """
        self.icon = graphics["icon"]
        self.plain_graphic = graphics["plain"]
        self.chopped_graphic = graphics["chopped"]
        self.chopped_icon = graphics["chopped_icon"]
        self.plated_icon = graphics["plated_icon"]
        self.fried_graphic = graphics["fried"]
        self.fried_icon = graphics["fried_icon"]
        self.chopped = False
        self.fried = False
        self.place = place
        self.position = None
        self.image = None
        self.rect = None
        super().__init__()
        Resources.add(self)
        
    def determine_position(self):
        """Determine and update the position and image of the resource based on its place and state.
        
        The position, image, and rect are updated depending on whether the resource is with a Player, on a CounterTop, or on a Plate. For Plates, ingredient subicons are also positioned.
        """
        if(self.place.__class__.__name__ == 'Player'):
            player = self.place
            self.position = (player.rect.center[0] + 20, player.rect.center[1] - 20)
            self.image = self.icon
            if(self.chopped):
                self.image = self.chopped_icon
            if(self.fried):
                self.image = self.fried_icon
            self.rect = self.image.get_rect(center = self.position)
            
        if(isinstance(self.place, CounterTop)):
            table = self.place
            self.position = table.rect.center
            self.image = self.plain_graphic
            if(self.chopped):
                self.image = self.chopped_graphic
            if(self.fried):
                self.image = self.fried_graphic
            self.rect = self.image.get_rect(center = self.position)
        
        if(isinstance(self.place, Plate)):
            pass #Its position is determined when the position of the place is determined - see below:
        
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
            
    def chop(self):
        """Mark the resource as chopped."""
        self.chopped = True
        
    def fry(self):
        """Mark the resource as fried."""
        self.fried = True
        
    

class Fish(Resource):
    def __init__(self, place):
        """Initialize a Fish resource.
        
        Parameters:
            place: The initial location of the fish resource.
        """
        super().__init__(FISH_GRAPHICS, place)

class Potato(Resource):
    def __init__(self, place):
        """Initialize a Potato resource.
        
        Parameters:
            place: The initial location of the potato resource.
        """
        super().__init__(POTATO_GRAPHICS, place)
        
class Plate(Resource):
    def __init__(self, place):
        """Initialize a Plate resource used for assembling dishes.
        
        Parameters:
            place: The initial location of the plate resource.
        """
        super().__init__(PLATE_GRAPHICS, place)
        self.dish = []
        self.dish_dict = {"Fish": 0, "Potato": 0}
    
    def add_ingredient(self, ingredient):
        """Add an ingredient to the plate and update the dish dictionary accordingly.
        
        Parameters:
            ingredient: The resource to add as an ingredient to the dish.
        """
        self.dish.append(ingredient)
        ingredient.place = self
        if isinstance(ingredient, Fish):
            self.dish_dict["Fish"] += 1
        if isinstance(ingredient, Potato):
            self.dish_dict["Potato"] += 1
    
    def kill(self):
        """Remove all ingredients from the plate and kill the plate resource.
        
        Calls kill() on all ingredients before calling the superclass kill method.
        """
        for ingredient in self.dish:
            ingredient.kill()
        super().kill()

        
        