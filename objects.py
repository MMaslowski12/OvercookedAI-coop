import pygame
from constants import FLOOR_GRAPHIC, WALL_GRAPHIC, COUNTERTOP_ICON, CB_ICON, CB_KNIFELESS_ICON, CB_R_ICON, CB_R_KNIFELESS_ICON, FRYER_ICON, WAITER_POINT, TRASH_CAN, GREEN, BLACK
import math
from constants import screen

class Object(pygame.sprite.Sprite):
    def __init__(self, position, graphic):
        """Initialize the Object with a position and graphic.
        
        Parameters:
            position (tuple): The center coordinates of the object.
            graphic: The image surface representing the object.
        """
        super().__init__()
        self.image = graphic
        self.rect = self.image.get_rect(center=position)
        
    def check_distance(self, object2):
        """Calculate the Euclidean distance between this object and another.
        
        Parameters:
            object2: Another Object instance.
        
        Returns:
            float: The distance between the centers of the two objects.
        """
        x1, y1 = self.rect.centerx, self.rect.centery
        x2, y2 = object2.rect.centerx, object2.rect.centery
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
Floors = pygame.sprite.Group()
class Floor(Object):
    def __init__(self, position):
        """Initialize a Floor object at the specified position.
        
        Parameters:
            position (tuple): The center coordinates for this floor.
        """
        super().__init__(position, FLOOR_GRAPHIC)
        Floors.add(self)

Walls = pygame.sprite.Group()
class Wall(Object):
    def __init__(self, position, graphic = WALL_GRAPHIC):
        """Initialize a Wall object with a given position and graphic.
        
        Parameters:
            position (tuple): The center coordinates of the wall.
            graphic: The image representing the wall (default: WALL_GRAPHIC).
        """
        super().__init__(position, graphic)
        Walls.add(self)


Sources = pygame.sprite.Group()
class ResourceSource(Wall):
    def __init__(self, position, resource, graphic):
        """Initialize a resource source that provides a resource.
        
        Parameters:
            position (tuple): The center coordinates of the source.
            resource: The resource to be provided.
            graphic: The graphic representing the source.
        """
        super().__init__(position, graphic)
        self.resource = resource
        Sources.add(self)
        Walls.add(self)
    
    def give_resource(self, player):
        """Provide a resource to the specified player.
        
        Parameters:
            player: The player instance that will receive the resource.
        """
        player.hands = self.resource(player)
        
CounterTops = pygame.sprite.Group()
class CounterTop(Wall):
    def __init__(self, position, graphic = COUNTERTOP_ICON, resource = None):
        """Initialize a CounterTop with an optional resource.
        
        Parameters:
            position (tuple): The center coordinates of the countertop.
            graphic: The icon representing the countertop (default: COUNTERTOP_ICON).
            resource: The resource placed on the countertop (default: None).
        """
        super().__init__(position, graphic)
        Walls.add(self)
        CounterTops.add(self)
        self.resource = resource
        
    def put_resource(self, resource):
        """Place a resource onto the countertop.
        
        Parameters:
            resource: The resource to place on the countertop.
        """
        self.resource = resource
        resource.place = self
        
    def remove_resource(self):
        """Remove the resource from the countertop."""
        self.resource = None
        
CBoards = pygame.sprite.Group()
class CBoard(CounterTop):
    def __init__(self, position, resource = None, graphic = CB_ICON):
        """Initialize a chopping board (CBoard) with an optional resource.
        
        Parameters:
            position (tuple): The center coordinates of the chopping board.
            resource: The resource on the board (default: None).
            graphic: The icon representing the board (default: CB_ICON).
        """
        super().__init__(position, graphic, resource)
        self.chopping = False
        self.chopper = None
        self.progress = 0
        self.progress_max = 300
        CBoards.add(self)

    def adjust_knife(self):
        """Toggle the knife graphic on the chopping board."""
        if(self.image == CB_ICON):
            self.image = CB_KNIFELESS_ICON
            
        elif(self.image == CB_KNIFELESS_ICON):
            self.image = CB_ICON
            
        elif(self.image == CB_R_ICON):
            self.image = CB_R_KNIFELESS_ICON
            
        elif(self.image == CB_R_KNIFELESS_ICON):
            self.image = CB_R_ICON
        
        
    def put_resource(self, resource):
        """Place a resource on the chopping board and adjust the knife graphic.
        
        Parameters:
            resource: The resource to be placed on the board.
        """
        super().put_resource(resource)
        self.adjust_knife()
    
    def remove_resource(self):
        """Remove the resource from the chopping board and reset chopping progress."""
        super().remove_resource()
        self.progress = 0
        self.adjust_knife()
    
    def start_chopping(self, player):
        """Begin the chopping process with the given player.
        
        Parameters:
            player: The player initiating the chopping.
        """
        self.chopping = True
        self.chopper = player

    def stop_chopping(self):
        """Stop the chopping process and clear the active chopper."""
        self.chopping = False
        self.chopper = None

    def update(self):
        """Update the state of the chopping board by processing chopping progress.
        
        Increases progress if a player is actively chopping until completion, then finalizes the chopping.
        """
        if(self.resource != None):
            if(self.resource.chopped == False):
                self.draw_progress_bar()
            
        if (not self.chopping):
            return None
        
        #If a chopper is still chopping
        if(self.chopper.action == self):
            self.progress += 1
            if self.progress >= self.progress_max:
                self.progress = self.progress_max
                self.stop_chopping()
                self.resource.chop()
        else:
            self.stop_chopping
                
        

    def draw_progress_bar(self):
        """Display a progress bar indicating the current chopping progress."""
        bar_length = 50
        bar_height = 10
        fill = (self.progress / self.progress_max) * bar_length
        pygame.draw.rect(screen, GREEN, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, fill, bar_height])
        pygame.draw.rect(screen, BLACK, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, bar_length, bar_height], 2)
        
Fryers = pygame.sprite.Group()
class Fryer(CounterTop):
    def __init__(self, position, resource = None, graphic = FRYER_ICON):
        """Initialize a Fryer with an optional resource.
        
        Parameters:
            position (tuple): The center coordinates of the fryer.
            resource: The resource to be fried (default: None).
            graphic: The icon representing the fryer (default: FRYER_ICON).
        """
        super().__init__(position, graphic, resource)
        self.frying = False
        self.fried = False
        self.frier = None
        self.progress = 0
        self.progress_max = 300
        Fryers.add(self)
        
    
    def start_frying(self):
        """Begin the frying process."""
        self.frying = True

    def stop_frying(self):
        """Stop the frying process."""
        self.frying = False
        
    def remove_resource(self):
        """Remove the resource from the fryer and reset frying progress."""
        super().remove_resource()
        self.progress = 0

    def update(self):
        """Update the state of the fryer by processing frying progress.
        
        Increases progress until the resource is fully fried, then stops frying.
        """
        if(self.resource != None):
            if(self.resource.fried == False):
                self.draw_progress_bar()
            
        if (not self.frying):
            return None
        
        #If a chopper is still chopping
        self.progress += 1
        if self.progress >= self.progress_max:
            self.progress = self.progress_max
            self.stop_frying()
            self.resource.fry()
                
        

    def draw_progress_bar(self):
        """Display a progress bar indicating the current frying progress."""
        bar_length = 50
        bar_height = 10
        fill = (self.progress / self.progress_max) * bar_length
        pygame.draw.rect(screen, GREEN, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, fill, bar_height])
        pygame.draw.rect(screen, BLACK, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, bar_length, bar_height], 2)

CBelts = pygame.sprite.Group()
class CBelt(CounterTop):
    def __init__(self, menu, position, graphic = WAITER_POINT):
        """Initialize a conveyor belt (CBelt) for serving dishes.
        
        Parameters:
            menu: The menu instance for handling served dishes.
            position (tuple): The center coordinates of the belt.
            graphic: The icon representing the belt (default: WAITER_POINT).
        """
        super().__init__(position, graphic)
        self.menu = menu
        CBelt.add(self)
        
    def put_resource(self, resource):
        """Serve a dish by transferring the resource through the menu and remove the resource afterwards.
        
        Parameters:
            resource: The resource (dish) to be served.
        """
        self.menu.serve_dish(resource)
        resource.kill()

class TrashCan(CBelt):
    def __init__(self, menu, position, graphic = TRASH_CAN):
        """Initialize a TrashCan for discarding resources.
        
        Parameters:
            menu: The menu instance (not used for trash can operations).
            position (tuple): The center coordinates of the trash can.
            graphic: The icon representing the trash can (default: TRASH_CAN).
        """
        super().__init__(menu, position, graphic)
    
    #Overriding - same as CBelt, but without registering the dish
    def put_resource(self, resource):
        """Discard the resource without serving it through the menu.
        
        Parameters:
            resource: The resource to be discarded.
        """
        resource.kill()

