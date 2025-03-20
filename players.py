import pygame
from constants import *
from foods import Plate
from objects import Object, Sources, CounterTops, CBoard, Fryer, Walls, CBelt, TrashCan
import math

Players = pygame.sprite.Group()
class Player(Object):
    def __init__(self, position, player_graphic, controls):
        """Initialize a Player instance with a starting position, graphic, and control mapping.
        
        Parameters:
            position (tuple): The starting (x, y) coordinates of the player.
            player_graphic: The visual representation of the player.
            controls (dict): Mapping of action names to pygame key constants.
        """
        super().__init__(position, player_graphic)
        self.controls = controls
        self.hands = None
        self.speed = PLAYER_SPEED
        self.action = None
        self.HAND_LENGTH = SIZE * math.sqrt(2) - 5 #Slightly smaller than allowing you to get it with a 45 degree angle
        self.action_cooldown = 0
        Players.add(self)
        
    
    def update(self, keys):
        """Update the player's state based on key inputs.
        
        Processes movement and actions such as grabbing resources, putting them down, chopping, frying, or taking from a table.
        
        Parameters:
            keys: A sequence or mapping representing the current key states from pygame.key.get_pressed().
        """
        #Actions - grabbing a resource, putting down a reource; only one action can be done in one update
        self.action_cooldown -= 1
        if(keys[self.controls['ACTION']] & isinstance(self.action, CBoard)):
           pass
        else:
           self.action = None 
            
        if (keys[self.controls['ACTION']] & (self.action_cooldown <= 0)):
            action_made = False
            for source in Sources:
                if(not action_made):
                    action_made = action_made or self.grab_resource(source)
            
            for countertop in CounterTops:
                if (not action_made):
                    action_made = action_made or self.put_down_resource(countertop)
                    
                if(isinstance(countertop, CBoard)):
                    if (not action_made):
                        action_made = action_made or self.chop(countertop)
                
                if(isinstance(countertop, Fryer)):
                    if (not action_made):
                        action_made = action_made or self.fry(countertop)
                
                if (not action_made):
                    action_made = action_made or self.take_resource_from_table(countertop)
                    
                    
            if(action_made):
                self.action_cooldown = 10
                    
        
        #Move up down, left, or right
        self.moved = False
        prex, prey = self.rect.x, self.rect.y
        if keys[self.controls['UP']]:
            self.rect.y -= self.speed
            self.moved = True
            
        if keys[self.controls['DOWN']]:
            self.rect.y += self.speed
            self.moved = True
            
        if keys[self.controls['LEFT']]:
            self.rect.x -= self.speed
            self.moved = True
            
        if keys[self.controls['RIGHT']]:
            self.rect.x += self.speed
            self.moved = True
            
        self.last_move = (self.rect.x - prex, self.rect.y - prey)
        if(self.moved):
            self.check_collision()
            
    
    def bounce_back(self):
        """Revert the player's position to its previous state if a collision is detected.
        
        This subprocedure resets the player's position using the last recorded movement delta.
        """
        self.rect.x, self.rect.y = self.rect.x - self.last_move[0], self.rect.y - self.last_move[1]
        
        
    def check_collision(self):
        """Detect collisions with walls and other players, and undo the move if necessary.
        
        Checks collision using pygame's spritecollide and rect collision with other players.
        """
        collisions = pygame.sprite.spritecollide(self, Walls, False)
        if(collisions):
            self.bounce_back()
            
        players = 0
        for player in Players:
            if(self.rect.colliderect(player)):
                players += 1
                
        assert(players > 0)
        if(players > 1):
            self.bounce_back()
    
    def grab_resource(self, source):
        """Attempt to grab a resource from a given source if within reach and if hands are empty.
        
        Parameters:
            source: The resource provider object from which to attempt grabbing a resource.
        
        Returns:
            bool: True if a resource is successfully grabbed, otherwise False.
        """
        if ((self.check_distance(source) < self.HAND_LENGTH) & (self.hands == None)):
            source.give_resource(self)
            return True
        
        return False
            
    def put_down_resource(self, table):
        """Attempt to place the held resource onto a table if conditions allow.
        
        Checks if the table is within reach and if the player's hands are not empty, and then verifies specific conditions based on table type.
        
        Parameters:
            table: The table or countertop object on which to attempt placing the resource.
        
        Returns:
            bool: True if the resource is successfully put down, otherwise False.
        """
        #Allow only scenarios where the table is within reach and hands are not empty        
        if(self.hands == None or self.check_distance(table) >= self.HAND_LENGTH):
            return False
        
        #Adding on an empty table
        if (table.resource == None):
            condition = True
            #To put it on a fryer, it must be chopped
            if(isinstance(table, Fryer) and not self.hands.chopped):
                condition = False

            if(isinstance(table, TrashCan)):
                print("TRASH CAN")
                print(isinstance(table, CBelt))
                print(isinstance(table, TrashCan))
                print(isinstance(self.hands, Plate))

            if((isinstance(table, CBelt)) and (not isinstance(table, TrashCan)) and (not isinstance(self.hands, Plate))):
                print("CANNOT GIVE THE POTATO")
                print(isinstance(table, CBelt))
                print(isinstance(table, TrashCan))
                print(isinstance(self.hands, Plate))
                condition = False

            if(isinstance(table, TrashCan)):
                print("END OF TRASH CAN")
                print(isinstance(table, CBelt))
                print(isinstance(table, TrashCan))
                print(isinstance(self.hands, Plate))
            
                
            if(isinstance(self.hands, Plate) and (isinstance(table, Fryer) or isinstance(table, CBoard))):
                condition = False
            
            if(condition):
                table.put_resource(self.hands)
                self.hands = None
                return True
            return False
        
        #Adding on a plate
        elif (isinstance(table.resource, Plate) and not isinstance(self.hands, Plate) and self.hands.fried):
            table.resource.add_ingredient(self.hands)
            self.hands = None
            return True

        return False

    def take_resource_from_table(self, table):
        """Attempt to take a resource from a table if within reach and if the player's hands are empty.
        
        Validates that the resource meets conditions based on the table's type (e.g., chopped for a chopping board, fried for a fryer) before taking it.
        
        Parameters:
            table: The table or countertop object from which to attempt taking the resource.
        
        Returns:
            bool: True if the resource is successfully taken, otherwise False.
        """
        if ((self.check_distance(table) < self.HAND_LENGTH) & (self.hands == None) & (table.resource != None)):
            condition = True
            if(isinstance(table, CBoard)):
                condition = table.resource.chopped
                
            if(isinstance(table, Fryer)):
                condition = table.resource.fried
                
            if(condition):
                self.hands = table.resource
                table.resource.place = self
                table.remove_resource()
                return True
            else:
                return False
        
        return False

    def chop(self, CB):
        """Attempt to initiate chopping of a resource on a chopping board if within reach.
        
        Verifies that the resource is not already chopped and that the player's hands are empty before starting the chopping action.
        
        Parameters:
            CB: The chopping board object on which to attempt chopping.
        
        Returns:
            bool: True if chopping is initiated, otherwise False.
        """
        if ((self.check_distance(CB) < self.HAND_LENGTH) & (CB.resource != None) & (self.hands == None)):
            if(CB.resource.chopped):
                return False
            CB.start_chopping(self)
            self.action = CB
            return True
        return False
    
    def fry(self, Fryer):
        """Attempt to initiate frying of a resource using a fryer if within reach.
        
        Checks that the resource is not already fried or in the process of frying and that the player's hands are empty before starting the frying action.
        
        Parameters:
            Fryer: The fryer object to use for frying.
        
        Returns:
            bool: True if frying is initiated, otherwise False.
        """
        if ((self.check_distance(Fryer) < self.HAND_LENGTH) & (Fryer.resource != None) & (self.hands == None)):
            if(Fryer.resource.fried or Fryer.frying):
                return False
            
            Fryer.start_frying()
            return True
        return False
        
    
