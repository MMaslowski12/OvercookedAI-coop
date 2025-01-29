import pygame
from Objects import Object
from Foods import Plate, Potato, Fish
from constants import PLAYER1_GRAPHIC, PLAYER2_GRAPHIC

class Player(Object):
    HAND_LENGTH = 1620 #roughly (32*sqrt(2) - 5)^2
    def __init__(self, position, graphic, controls, board):
        super().__init__(position, graphic=graphic, board=board)
        self.controls = controls
        self.hands = None
        self.speed = 4
        self.chopping = None
        self.HAND_LENGTH = Player.HAND_LENGTH
        self.action_cooldown = 0
    
    def is_player(self):
        return True
    
    def action_possible(self): #Thats ugly but oh well
        Interactables = self.board.Interactables
        for interactable in Interactables: #How do I get the Interactables? Either pass it as an argument or add it to the initialization. I mean somewhere else I ask to get nonpassables
            if (self.check_distance(interactable) < self.HAND_LENGTH):
                interactions = interactable.get_actions()
                for interaction in interactions:
                    if interaction(self, execute=False):
                        return interaction
                
        return None
        
    def _move(self, keys):
        dxdys = {"UP": (0, -1),
                "DOWN": (0, 1),
                "LEFT": (-1, 0),
                "RIGHT": (1, 0)}
        
        moved = False
        for direction in dxdys.keys():
            if keys[self.controls[direction]]:
                moved = True
                dx, dy = dxdys[direction]
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
                
        return moved
    
    def update(self, **kwargs):      
        self.action_cooldown -= 1
        keys = kwargs["keys"]
        Board = kwargs["board"]
        Interactables = Board.Interactables
        NonPassables = Board.NonPassables
        Players = Board.Players
        
        if (keys[self.controls['ACTION']] & (self.action_cooldown <= 0)):
            self.chopping = None
            action = self.action_possible()
            if(action is not None):
                action(self, execute=True)
                self.action_cooldown = 20
                return 0 

        prex, prey = self.rect.x, self.rect.y 
        moved = self._move(keys)
        self.last_move = (self.rect.x - prex, self.rect.y - prey)
        if(moved):
            self.chopping = None
            self._check_collision(NonPassables, Players)
            
    
    #Get back to the former position if you collided with a wall or a player
    def _bounce_back(self):
        self.rect.x, self.rect.y = self.rect.x - self.last_move[0], self.rect.y - self.last_move[1]
        
    #Check for collisions with Walls and the other players
    def _check_collision(self, NonPassables, Players):
        collisions = pygame.sprite.spritecollide(self, NonPassables, False)
        if(collisions):
            self._bounce_back()
            
        players = 0
        for player in Players:
            if(self.rect.colliderect(player)):
                players += 1
                
        assert(players > 0)
        if(players > 1):
            self._bounce_back()
        
    def get_state(self):
        '''
        Returns a list of:
        - coordinates of the Player:
            - 0: x coordinates of the Player
            - 1: y coordinates of the Player
        - 7 binary values describing Player's inventory. In respective order, these are values for whether the following is in Player's hands:
            - 2: Plate
            - 3: Raw Fish
            - 4: Cut Fish
            - 5: Fried Fish
            - 6: Raw Potato
            - 7: Cut Potato
            - 8: Fried Potato
        '''
        numerical_data = [0]*9
        numerical_data[0] = self.rect.x
        numerical_data[1] = self.rect.y
        
        if(self.hands == None):
            return numerical_data
        
        hand = self.hands
        
        if(isinstance(hand, Plate)):
            numerical_data[2] = 1
            numerical_data[5] = hand.dish_dict['Fish']
            numerical_data[8] = hand.dish_dict['Potato']
                
        else:
            if isinstance(hand, Fish):
                if not hand.chopped:
                    numerical_data[3] = 1
                
                elif not hand.fried:
                    numerical_data[4] = 1
                
                else: numerical_data[5] = 1
            
            else:
                if not hand.chopped:
                    numerical_data[6] = 1
                
                elif not hand.fried:
                    numerical_data[7] = 1
                
                else: numerical_data[8] = 1
                       
        return numerical_data
        
class Player1(Player):
    def __init__(self, position, board):
        player1_controls = {
            "UP": pygame.K_w,
            "DOWN": pygame.K_s,
            "LEFT": pygame.K_a,
            "RIGHT": pygame.K_d,
            "ACTION": pygame.K_e
        }
        
        super().__init__(position=position, graphic=PLAYER1_GRAPHIC, controls=player1_controls, board=board)
        
class Player2(Player):
    def __init__(self, position, board):
        player2_controls = {
            "UP": pygame.K_UP,
            "DOWN": pygame.K_DOWN,
            "LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT,
            "ACTION": pygame.K_SPACE
        }
        
        super().__init__(position=position, graphic=PLAYER2_GRAPHIC, controls=player2_controls, board=board)

        
    
