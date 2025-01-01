import pygame
from constants import *
from Foods import Plate, Fish, Potato

def interaction_method(func):
    func.interaction_method = True
    return func

class Object(pygame.sprite.Sprite):    
    def __init__(self, position, graphic, board):
        super().__init__()
        self.image = graphic
        self.rect = self.image.get_rect(center=position)
        self.board = board
        
    def check_distance(self,object2):
        x1, y1 = self.rect.centerx, self.rect.centery
        x2, y2 = object2.rect.centerx, object2.rect.centery
        return (x2-x1)**2 + (y2-y1)**2 #Square of a distance
    
    def is_interactable(self):
        return False
    
    def is_nonpassable(self):
        return False
    
    def is_player(self):
        return False

class NonPassable(Object):    
    def __init__(self, position, graphic, board):
        super().__init__(position, graphic=graphic, board=board)
        
    def is_nonpassable(self):
        return True
        
class Interactable(Object):
    def __init__(self, position, graphic, board):
        super().__init__(position, graphic=graphic, board=board)
    
    def is_interactable(self):
        return True
    
    def get_actions(self):
        interactions = []
        for method_name in dir(self):
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if(method_name == "give_resource"):
                    print("FOR GIVE_RESOURCE: ", callable(method), getattr(method, "interaction_method", False))
                
                if callable(method) and getattr(method, "interaction_method", False):
                    print("xd2")
                    interactions.append(method)
                    
        return interactions
    
    def update(*args, **kwargs):
        pass 
                

class Floor(Object):
    def __init__(self, position, board):
        super().__init__(position, graphic=FLOOR_GRAPHIC, board=board)
        # Floors.add(self)

# Walls = pygame.sprite.Group()
class Wall(NonPassable):
    def __init__(self, position, board):
        super().__init__(position, graphic=WALL_GRAPHIC, board=board)
        # Walls.add(self)
        
# Sources = pygame.sprite.Group()
class ResourceSource(NonPassable, Interactable): #Add it to the Board whenever it's initialized, so whenever give_resource is executed. The problem: it needs to add it to the Board-level Group. So, it needs it as an argument? How else
    def __init__(self, position, food, graphic, board):
        super().__init__(position, graphic=graphic, board=board)
        self.food = food
        # Sources.add(self)
            
    # take the resource = player now has resource
    @interaction_method
    def give_resource(self, player, execute = True):
        print("Give resource")
        if (player.hands == None):
            if (execute):
                player.hands = self.food(player)
                
            return True
        
        return False
        
class FishCrate(ResourceSource):
    def __init__(self, position, board):
        super().__init__(position, Fish, graphic=FISH_CRATE_ICON, board=board)

class PotatoCrate(ResourceSource):
    def __init__(self, position, board):
        super().__init__(position, Potato, graphic=POTATO_CRATE_ICON, board=board)
        
class PlateCrate(ResourceSource):
    def __init__(self, position, board):
        super().__init__(position, Plate, graphic=PLATE_CRATE, board=board)
        
# CounterTops = pygame.sprite.Group()
class CounterTop(NonPassable, Interactable):
    def __init__(self, position, board, graphic=COUNTERTOP_ICON):
        super().__init__(position, graphic=graphic, board=board)
        # CounterTops.add(self)
        self.resource = None
    
    @interaction_method
    def put_resource(self, player, execute = True):        
        if(player.hands == None):
            return False
        
        #Adding on an empty table
        if (self.resource == None):
            #To put it on a fryer, it must be chopped
            if execute:
                self.resource = player.hands
                player.hands.place = self
                player.hands = None
                
            return True
    
        #Adding to a plate on a table
        else:
            plate_conditions = isinstance(self.resource, Plate) and (not isinstance(player.hands, Plate)) and player.hands.fried
            if plate_conditions and execute:
                self.resource.add_ingredient(self.hands)
                player.hands = None
                
            return plate_conditions

        
        
    @interaction_method
    def remove_resource(self, player, execute = True):
        if ((player.hands == None) & (self.resource != None)):
            condition = True                                
            if(condition):
                if execute:
                    player.hands = self.resource
                    self.resource.place = player
                    self.resource = None
                    
                return True
            
            else:
                return False
        
        return False
        
        
        
class CBoard(CounterTop):
    def __init__(self, position, board, graphic = CB_ICON):
        super().__init__(position, graphic=graphic, board=board)
        self.chopping = False
        self.chopper = None
        self.progress_increment = 0.33
        # CBoards.add(self)

    def draw(self, surface):
        #Overriden because of the progress bars 
        pygame.draw.rect(surface, self.image, self.rect)

        if (self.resource is not None):
            progress, bar = self.get_progress_bar(surface)
            pygame.draw.rect(*progress) #Unpack the tuple
            pygame.draw.rect(*bar)

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
        
        
    #Overriding
    @interaction_method
    def put_resource(self, player, execute = True):
        # Break down the condition into named variables
        has_hands = player.hands is not None
        table_is_empty = self.resource is None
        not_a_plate = not isinstance(player.hands, Plate)
        not_chopped = getattr(player.hands, "chopped", True) != True  # Default to True if 'chopped' doesn't exist
        
        condition = has_hands and table_is_empty and not_a_plate and not_chopped
        
        #Adding on an empty table
        if condition and execute:            
            self.resource = player.hands
            self.adjust_knife()
            player.hands.place = self
            player.hands = None
             
        return condition            
    
    @interaction_method
    def remove_resource(self, player, execute=True):
        condition = super().remove_resource(player, execute=False)
        condition = condition and self.resource.chopped
        if condition and execute:
            super().remove_resource(player, execute)
            self.resource.progress = 0
            self.adjust_knife()
        
        return condition
    
    @interaction_method
    def start_chopping(self, player, execute = True):
        if ((player.resource != None) & (player.hands == None)):
            if(player.resource.chopped):
                return False
            
            if execute:
                player.chopping = self
                self.chopper = player
                
            return True
        return False    
    
    def chop(self):
        self.resource.progress += self.progress_increment
        if self.resource.progress >= self.progress_max:
            self.resource.progress = 0
            self.chopping = False
            self.resource.chop()

    def update(self): #SEE WHAT ACTION THE PLAYER FROM BEFORE MAKES NOW
        if(self.chopper != None):
            if(self.chopper.chopping == self):
                self.chop()
        
        if(self.resource != None):
            if(self.resource.chopped == False):
                self.draw_progress_bar()
            
        if (not self.chopping):
            return None
        
    def get_progress_bar(self, screen):
        bar_length = 50 #Should be 50
        bar_height = 10
        fill = (self.resource.progress / self.progress_max) * bar_length
        progress = (screen, GREEN, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, fill, bar_height])
        bar = (screen, BLACK, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, bar_length, bar_height], 2)
        return progress, bar
        
# Fryers = pygame.sprite.Group()
class Fryer(CounterTop):
    def __init__(self, position, board, graphic = FRYER_ICON):
        super().__init__(position, graphic=graphic, board=board)
        self.progress_bar_rectangles = []
        self.frying = False
        self.fried = False
        self.frier = None
        self.progress_increment = 0.33
        # Fryers.add(self)
        
    def draw(self, surface):
        #Overriden because of the progress bars 
        pygame.draw.rect(surface, self.image, self.rect)

        if (self.resource is not None):
            progress, bar = self.get_progress_bar(surface)
            pygame.draw.rect(*progress) #Unpack the tuple
            pygame.draw.rect(*bar)
    
    @interaction_method
    def start_frying(self, player, execute = True):
        if ((self.resource != None) & (player.hands == None)):
            if(player.resource.fried or self.frying):
                return False
            
            if execute:
                self.frying = True
            
            return True
        return False
        
    #Overriding
    @interaction_method
    def put_resource(self, player, execute = True):
        # Break down the condition into named variables
        has_hands = player.hands is not None
        table_is_empty = self.resource is None
        not_a_plate = not isinstance(player.hands, Plate)
        is_chopped = getattr(player.hands, "chopped", False) == True  # Default to True if 'chopped' doesn't exist
        not_fried = getattr(player.hands, "fried", True) != True  # Default to True if 'chopped' doesn't exist
        
        condition = has_hands and table_is_empty and not_a_plate and is_chopped and not_fried
        
        #Adding on an empty table
        if condition:            
            if execute:
                self.resource = player.hands
                player.hands.place = self
                player.hands = None
                            
        return condition          
        
    @interaction_method
    def remove_resource(self, player, execute):
        #MODIFIED TO ADD A CONDITION THAT A RESOURCE MUST BE CHOPPED
        condition = super().remove_resource(player, execute=False)
        condition = condition and self.resource.Fried
        if condition:
            super().remove_resource(player, execute)
            if execute:
                self.resource.progress = 0
                return True
        
        return False
        

    def update(self): #SEE WHAT ACTION THE PLAYER FROM BEFORE MAKES 
        if (self.frying):
            self.resource.progress += self.progress_increment
            if self.resource.progress >= 100:
                self.resource.progress = 0
                self.frying = False
                self.resource.fry()
                
        if(self.resource != None):
            if(self.resource.fried == False):
                self.draw_progress_bar()
            
        if (not self.frying):
            return None

    def get_progress_bar(self, screen):
        bar_length = 50 #Should be 50
        bar_height = 10
        fill = (self.resource.progress / self.progress_max) * bar_length
        progress = (screen, GREEN, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, fill, bar_height])
        bar = (screen, BLACK, [self.rect.x + 16 - bar_length/2, self.rect.y - 20, bar_length, bar_height], 2)
        return progress, bar
        
class CBelt(CounterTop):
    def __init__(self, position, board, graphic = WAITER_POINT):
        super().__init__(position, graphic=graphic, board=board)
        # CBelt.add(self)
        
    @interaction_method
    def put_resource(self, player, execute):
        condition = super().put_resource(player, execute=False)
        condition = condition
        if not condition: #Like this because isinstance player.hands, Plate requires player.hands to not be none
            return False
        
        condition = condition and isinstance(player.hands, Plate)
        #Can only serve food on a plate
        if (condition and execute):
            resource = player.hands
            self.board.Menu.serve_dish(resource)
            [x.kill() for x in resource.dish]
            resource.kill()
        
        return condition

class TrashCan(CounterTop):
    def __init__(self, position, board, graphic = TRASH_CAN):
        super().__init__(position, board=board, graphic=graphic)
    
    @interaction_method
    #Overriding - same as CBelt, but without registering the dish
    def put_resource(self, resource):
        if(isinstance(resource, Plate)):
            for x in resource.dish:
                x.place = None
                x.kill()
            
        resource.place = None
        resource.kill()


        
