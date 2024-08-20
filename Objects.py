import pygame
from constants import *
import math

class Object(pygame.sprite.Sprite):
    def __init__(self, position, graphic):
        super().__init__()
        self.image = graphic
        self.rect = self.image.get_rect(center = position)
        
    def check_distance(self,object2):
        x1, y1 = self.rect.centerx, self.rect.centery
        x2, y2 = object2.rect.centerx, object2.rect.centery
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
Floors = pygame.sprite.Group()
class Floor(Object):
    def __init__(self, position):
        super().__init__(position, FLOOR_GRAPHIC)
        Floors.add(self)

Walls = pygame.sprite.Group()
class Wall(Object):
    def __init__(self, position, graphic = WALL_GRAPHIC):
        super().__init__(position, graphic)
        Walls.add(self)
        
Sources = pygame.sprite.Group()
class ResourceSource(Wall):
    def __init__(self, position, resource, graphic):
        super().__init__(position, graphic)
        self.resource = resource
        Sources.add(self)
        Walls.add(self)
    
    # take the resource = player now has resource
    def give_resource(self, player):
        player.hands = self.resource(player)
        
CounterTops = pygame.sprite.Group()
class CounterTop(Wall):
    def __init__(self, position, graphic = COUNTERTOP_ICON, resource = None):
        super().__init__(position, graphic)
        Walls.add(self)
        CounterTops.add(self)
        self.resource = resource
        
    def put_resource(self, resource):
        self.resource = resource
        resource.place = self
        
    def remove_resource(self):
        self.resource = None
        
CBoards = pygame.sprite.Group()
class CBoard(CounterTop):
    def __init__(self, position, resource = None, graphic = CB_ICON):
        super().__init__(position, graphic, resource)
        self.chopping = False
        self.chopper = None
        self.progress = 0
        self.progress_max = 300
        CBoards.add(self)

    #Remove knife if there was a knife, add a knife if there was no knife
    def adjust_knife(self):
        if(self.image == CB_ICON):
            self.image = CB_KNIFELESS_ICON
            
        elif(self.image == CB_KNIFELESS_ICON):
            self.image = CB_ICON
            
        elif(self.image == CB_R_ICON):
            self.image = CB_R_KNIFELESS_ICON
            
        elif(self.image == CB_R_KNIFELESS_ICON):
            self.image = CB_R_ICON
        
        
    #Overriding to add the removal of a knife
    def put_resource(self, resource):
        super().put_resource(resource)
        self.adjust_knife()
    
    def remove_resource(self):
        super().remove_resource()
        self.progress = 0
        self.adjust_knife()
    
    def start_chopping(self, player):
        self.chopping = True
        self.chopper = player

    def stop_chopping(self):
        self.chopping = False
        self.chopper = None

    def update(self): #SEE WHAT ACTION THE PLAYER FROM BEFORE MAKES NOW
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
        bar_length = 50
        bar_height = 10
        fill = (self.progress / self.progress_max) * bar_length
        pygame.draw.rect(screen, GREEN, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, fill, bar_height])
        pygame.draw.rect(screen, BLACK, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, bar_length, bar_height], 2)
        
Fryers = pygame.sprite.Group()
class Fryer(CounterTop):
    def __init__(self, position, resource = None, graphic = FRYER_ICON):
        super().__init__(position, graphic, resource)
        self.frying = False
        self.fried = False
        self.frier = None
        self.progress = 0
        self.progress_max = 300
        Fryers.add(self)
        
    
    def start_frying(self):
        self.frying = True

    def stop_frying(self):
        self.frying = False
        
    def remove_resource(self):
        super().remove_resource()
        self.progress = 0

    def update(self): #SEE WHAT ACTION THE PLAYER FROM BEFORE MAKES NOW
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
        bar_length = 50
        bar_height = 10
        fill = (self.progress / self.progress_max) * bar_length
        pygame.draw.rect(screen, GREEN, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, fill, bar_height])
        pygame.draw.rect(screen, BLACK, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, bar_length, bar_height], 2)
        
CBelts = pygame.sprite.Group()
class CBelt(CounterTop):
    def __init__(self, position, graphic = WAITER_POINT):
        super().__init__(position, graphic)
        CBelt.add(self)
        
    def put_resource(self, resource):
        #Can only serve food on a plate
        if(not isinstance(resource, Plate)):
            return 0
        
        if(isinstance(resource, Plate)):
            if(Menu.serve_dish(resource)):
                [x.kill() for x in resource.dish]
                resource.kill()

class TrashCan(CBelt):
    def __init__(self, position, graphic = TRASH_CAN):
        super().__init__(position, graphic)
    
    #Overriding - same as CBelt, but without registering the dish
    def put_resource(self, resource):
        if(isinstance(resource, Plate)):
            [x.kill() for x in resource.dish]
            
        resource.kill()


        
