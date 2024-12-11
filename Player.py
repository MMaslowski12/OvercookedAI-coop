import pygame
import math
from constants import SIZE
from Objects import Object, Walls, CBoard, Fryer, Sources, CounterTops
from Foods import Plate, Potato, Fish
import numpy as np

Players = pygame.sprite.Group()
class Player(Object):
    def __init__(self, position, player_graphic, controls):
        super().__init__(position, player_graphic)
        self.controls = controls
        self.hands = None
        self.speed = 4
        self.chopping = None
        self.HAND_LENGTH = SIZE * math.sqrt(2) - 5 #Slightly smaller than allowing you to get it with a 45 degree angle
        self.action_cooldown = 0
        Players.add(self)
        

    
    def action_possible(self):
        for source in Sources:
            if self.grab_resource(source, execute = False):
                return {"action": self.grab_resource, "input": source}
            
        for countertop in CounterTops:
            if self.put_down_resource(countertop, execute=False):
                return {"action": self.put_down_resource, "input": countertop}
                
            if(isinstance(countertop, CBoard)):
                if self.chop(countertop, execute=False):
                    return {"action": self.chop, "input": countertop}
            
            if(isinstance(countertop, Fryer)):
                if self.fry(countertop, execute=False):
                    return {"action": self.fry, "input": countertop}
            
                
            if self.take_resource_from_table(countertop, execute=False):
                return {"action": self.take_resource_from_table, "input": countertop}    
                
        return {"action": None, "input": None}
        
        
        
    def update(self, keys):       
        self.action_cooldown -= 1
         
        if (keys[self.controls['ACTION']] & (self.action_cooldown <= 0)):
            self.chopping = None
            action_dict = self.action_possible()
            if(action_dict["action"] != None):
                action_dict["action"](action_dict["input"])
                self.action_cooldown = 20
                return 0 
                

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
            self.chopping = None
            self.check_collision()
            
    
    #Get back to the former position if you collided with a wall or a player
    def bounce_back(self):
        self.rect.x, self.rect.y = self.rect.x - self.last_move[0], self.rect.y - self.last_move[1]
        
        
    #Check for collisions with Walls and the other players
    def check_collision(self):
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
    
    #See if the resource source is close enough and if so, grab a resource
    def grab_resource(self, source, execute = True):
        if ((self.check_distance(source) < self.HAND_LENGTH) & (self.hands == None)):
            if (execute):
                source.give_resource(self)
            return True
        
        return False
            
    #See if the countertop is close enough and if so, put down a resource   
    def put_down_resource(self, table, execute = True):
        #Allow only scenarios where the table is within reach and hands are not empty        
        if(self.hands == None or self.check_distance(table) >= self.HAND_LENGTH):
            return False
        
        #Adding on an empty table
        if (table.resource == None):
            condition = True
            #To put it on a fryer, it must be chopped
            if (isinstance(table, Fryer) and not self.hands.chopped):
                condition = False
                
            if (isinstance(table, CBoard) and self.hands.chopped):
                condition = False
                
            if (isinstance(self.hands, Plate) and (isinstance(table, Fryer) or isinstance(table, CBoard))):
                condition = False
            
            if(condition):
                if execute:
                    table.put_resource(self.hands)
                    self.hands = None
                return True
            return False
        
        #Adding on a plate
        elif (isinstance(table.resource, Plate) and not isinstance(self.hands, Plate) and self.hands.fried):
            if execute:
                table.resource.add_ingredient(self.hands)
                self.hands = None
                
            return True

        return False

    def take_resource_from_table(self, table, execute = True):
        if ((self.check_distance(table) < self.HAND_LENGTH) & (self.hands == None) & (table.resource != None)):
            condition = True
            if(isinstance(table, CBoard)):
                condition = condition and table.resource.chopped
                
            if(isinstance(table, Fryer)):
                condition = condition and table.resource.fried
                
            if(condition):
                if execute:
                    self.hands = table.resource
                    table.resource.place = self
                    table.remove_resource()
                return True
            
            else:
                return False
        
        return False

    def chop(self, CB, execute = True):
        if ((self.check_distance(CB) < self.HAND_LENGTH) & (CB.resource != None) & (self.hands == None)):
            if(CB.resource.chopped):
                return False
            if execute:
                self.chopping = CB
                CB.start_chopping(self)
                
            return True
        return False
    
    def fry(self, Fryer, execute = True):
        if ((self.check_distance(Fryer) < self.HAND_LENGTH) & (Fryer.resource != None) & (self.hands == None)):
            if(Fryer.resource.fried or Fryer.frying):
                return False
            
            if execute:
                Fryer.start_frying()
            
            return True
        return False
    
    def get_state(self):
        '''
        7 binary values describing Player's inventory. In respective order, these are values for whether the following is in Player's hands:
            - Plate
            - Raw Fish
            - Cut Fish
            - Fried Fish
            - Raw Potato
            - Cut Potato
            - Fried Potato
        '''
        numerical_data = np.zeros(shape=(7))
        
        if(self.hands == None):
            return numerical_data
        
        hand = self.hands
        
        if(isinstance(hand, Plate)):
            numerical_data[0] = 1
            numerical_data[3] = hand.dish_dict['Fish']
            numerical_data[6] = hand.dish_dict['Potato']
                
        else:
            if isinstance(hand, Fish):
                if not hand.chopped:
                    numerical_data[1] = 1
                
                elif not hand.fried:
                    numerical_data[2] = 1
                
                else: numerical_data[3] = 1
            
            else:
                if not hand.chopped:
                    numerical_data[4] = 1
                
                elif not hand.fried:
                    numerical_data[5] = 1
                
                else: numerical_data[6] = 1
                       
        return numerical_data
        
from Board import player1_start, player2_start
from constants import PLAYER1_GRAPHIC, PLAYER2_GRAPHIC

player1_controls = {
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "ACTION": pygame.K_e
}

player2_controls = {
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "ACTION": pygame.K_SPACE
}

Player1 = Player(player1_start, PLAYER1_GRAPHIC, player1_controls)
Player2 = Player(player2_start, PLAYER2_GRAPHIC, player2_controls) 
        
    
