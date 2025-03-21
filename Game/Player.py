import pygame
from .Objects import Object
from .Foods import Plate, Potato, Fish
from .constants import PLAYER1_GRAPHIC, PLAYER2_GRAPHIC
import numpy as np
import time

'''
TODO:

Test the game with human players

Implement the two models

Test the game with the two models

Test the learning

'''


class Player(Object):
    HAND_LENGTH = 1620 #roughly (32*sqrt(2) - 5)^2
    def __init__(self, position, graphic, controls, board, agent=None, misha_playing=False):
        """
        Initialize a Player.

        Args:
            position (tuple): The starting (x, y) position of the player.
            graphic: The graphic/sprite for the player.
            controls (dict): Dictionary mapping actions to pygame keys.
            board: The game board that the player exists on.
            agent: The learning agent (if any) controlling the player.
            misha_playing (bool): Flag to indicate if the agent is controlling the player.
        """
        super().__init__(position, graphic=graphic, board=board)
        self.controls = controls
        self.hands = None
        self.speed = 2
        self.chopping = None
        self.HAND_LENGTH = Player.HAND_LENGTH
        self.action_cooldown = 0
        self.Agent = agent
        self.time_actions = 0
        self.misha_playing = misha_playing
        self.time_saving = 0
        self.time_drawing = 0
        self.time_adding_experience = 0
        self.hit_the_wall_penalty = 0
        
    def is_player(self):
        """
        Check if this object is a player.

        Returns:
            bool: Always True for players.
        """
        return True
    
    def action_possible(self): #Thats ugly but oh well
        """
        Checks available actions based on proximity to interactable objects.

        Iterates through the board's interactables; if an interactable is close enough 
        and its available action returns True when checked, that action is considered possible.

        Returns:
            function or None: The first available action function or None if no action is possible.
        """
        Interactables = self.board.Interactables
        for interactable in Interactables: #How do I get the Interactables? Either pass it as an argument or add it to the initialization. I mean somewhere else I ask to get nonpassables
            if (self.check_distance(interactable) < self.HAND_LENGTH):
                interactions = interactable.get_actions()
                for interaction in interactions:
                    if interaction(self, execute=False):
                        return interaction
                
        return None
        
    def _move(self, actions):
        """
        Move the player based on the current key inputs.

        This method uses the movement keys from self.controls to adjust the player's position.
        After moving, it checks for collision with non-passable objects or other players, 
        and if a collision is detected, it reverts the movement.

        Args:
            keys (dict): Pygame key state dictionary.

        Returns:
            bool: True if the player moved, False otherwise.
        """
        NonPassables = self.board.NonPassables
        Players = self.board.Players

        moved = False
        dxdys = [(0, -1),
                (0, 1),
                (-1, 0),
                (1, 0)]
        
        moved = False
        for i in range(len(dxdys)):
            if actions[i]:
                dx, dy = dxdys[i]
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
                self.last_move = (dx*self.speed, dy*self.speed)
                xd = self._check_collision(NonPassables, Players)
                moved = moved or xd
                
        return moved
    
    def update(self, **kwargs): 
        """
        Update the player's state for the current frame.

        Decrease the action cooldown, check for action key press, trigger interactions if applicable,
        and move the player based on input keys.

        Args:
            **kwargs: Expected to contain 'keys' for current key states.
        """
        self.hit_the_wall_penalty = 0
        self.action_cooldown -= 1
        
        action = kwargs["actions"][4]
        if (action & (self.action_cooldown <= 0)):
            self.chopping = None
            action = self.action_possible()
            if action is not None:
                action(self, execute=True)
                self.action_cooldown = 20
                return 0 
                
        self._move(kwargs["actions"][:4])
        
                    
    #Get back to the former position if you collided with a wall or a player
    def _bounce_back(self):
        """
        Revert the player's position to its previous location upon collision.
        """
        self.rect.x, self.rect.y = self.rect.x - self.last_move[0], self.rect.y - self.last_move[1]
        self.hit_the_wall_penalty = -5
        
    #Check for collisions with Walls and the other players
    def _check_collision(self, NonPassables, Players):
        """
        Check for collisions with non-passable objects and other players.

        If a collision is detected, the player is bounced back to its previous position.

        Args:
            NonPassables: A collection of objects that the player cannot pass through.
            Players: A collection of other player objects.

        Returns:
            bool: True if a collision occurred, False otherwise.
        """
        collisions = pygame.sprite.spritecollide(self, NonPassables, False)
        if(collisions):
            self._bounce_back()
            return True
            
        players = 0
        for player in Players:
            if(self.rect.colliderect(player)):
                players += 1
                
        assert(players > 0)
        if(players > 1):
            self._bounce_back()
            return True

        return False
        
class Player1(Player):
    def __init__(self, position, board, agent=None, misha_playing=False):
        """
        Initialize Player1 with a specific control scheme.

        Args:
            position (tuple): Starting (x, y) position.
            board: The game board.
            agent: The learning agent (if any).
            misha_playing (bool): Whether the agent is controlling the player.
        """
        player1_controls = {
            "UP": pygame.K_w,
            "DOWN": pygame.K_s,
            "LEFT": pygame.K_a,
            "RIGHT": pygame.K_d,
            "ACTION": pygame.K_e
        }
        
        super().__init__(position=position, graphic=PLAYER1_GRAPHIC, controls=player1_controls, board=board, agent=agent, misha_playing=misha_playing)
        
class Player2(Player):
    def __init__(self, position, board, agent=None, misha_playing=False):
        """
        Initialize Player2 with a specific control scheme.

        Args:
            position (tuple): Starting (x, y) position.
            board: The game board.
            agent: The learning agent (if any).
            misha_playing (bool): Whether the agent is controlling the player.
        """
        player2_controls = {
            "UP": pygame.K_UP,
            "DOWN": pygame.K_DOWN,
            "LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT,
            "ACTION": pygame.K_SPACE
        }
        
        super().__init__(position=position, graphic=PLAYER2_GRAPHIC, controls=player2_controls, board=board, agent=agent, misha_playing=misha_playing)

        
    
