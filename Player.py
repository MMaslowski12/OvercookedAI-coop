import pygame
from Objects import Object
from Foods import Plate, Potato, Fish
from constants import PLAYER1_GRAPHIC, PLAYER2_GRAPHIC
import numpy as np
import time
import logging

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
        self.speed = 4
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
        
    def _move(self, keys):
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
        prex, prey = self.rect.x, self.rect.y 

        moved = False
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
        
        self.last_move = (self.rect.x - prex, self.rect.y - prey)
        if(moved):
            self.chopping = None
            if self._check_collision(NonPassables, Players):
                moved = False
                
        return moved
    
    def _get_mask(self):
        """
        Create an action mask based on available interactions.

        If an action is possible, the mask remains all ones. Otherwise, the mask disables the
        action corresponding to index 4 (last element).

        Returns:
            list: A mask list of 5 binary values.
        """
        if self.action_possible():
            mask = [1, 1, 1, 1, 1]
            
        else:
            mask = [1, 1, 1, 1, 0]
        
        return mask
    
    def idx2actions(self, idx):         
        """
        Convert an action index into a dictionary mapping pygame keys to booleans.

        Args:
            idx (int): The index corresponding to the key in self.controls.

        Returns:
            dict: Dictionary where only the key corresponding to the idx is set to True.
        """
        keys = [key for key in dir(pygame) if key.startswith('K_')]
        actions = {getattr(pygame, key): False for key in keys}
        
        actions[list(self.controls.values())[idx]] = True
        
        return actions
    
    def get_actions(self, state):
        """
        Determine the player's actions based on control mode.

        If controlled by an agent (misha_playing is True), query the agent's model.
        Otherwise, return the current pygame keys states.

        Args:
            state: The current state used by the agent for evaluation.

        Returns:
            dict or pygame key array: The action dictionary generated from agent or key inputs.
        """
        if (self.misha_playing):    
            _, idx = self.Agent.get_qs(state=state, mask=self._get_mask(), random_exploration=self.Agent.learning)    
            actions = self.idx2actions(idx)
        
        else:
            actions = pygame.key.get_pressed()
            # if self.debug and (self.tick % 180 == 0):
            #     self._debug_sonda()
        
        return actions
    
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
        
        keys = kwargs["keys"]
        if (keys[self.controls['ACTION']] & (self.action_cooldown <= 0)):
            self.chopping = None
            action = self.action_possible()
            if action is not None:
                action(self, execute=True)
                self.action_cooldown = 20
                return 0 
                
        self._move(keys)
        
    def remember_state_and_action(self, state, action_idx):
        """
        Stores the current state and the action index taken, 
        for later use in training the agent.

        Args:
            state: The current state representation.
            action_idx (int): The index of the action taken.
        """
        # logging.debug(f"former_visual_state shape: {self.former_visual_state.shape}")
        # logging.debug(f"former_numerical_state shape: {self.former_numerical_state.shape}")
        self.remembered_state = state
        self.remembered_action = action_idx
        
    def _reset_memory(self):
        """
        Reset the stored state and action memory.
        """
        self.remembered_state = None
        self.remembered_action = None
        
    def add_experience_to_batch(self, future_state, rewards):
        """
        Add the recent experience to the agent's batch memory.

        Combines the current remembered state and action with the future state and obtained rewards,
        and then delegates storing the experience to the agent's method.

        Args:
            future_state: The state after the current action.
            rewards (float): The rewards obtained from the transition.
        """
        state = self.remembered_state
        action = self.remembered_action
        future_mask = self._get_mask()
        #The state
        #The rewards
        #The action
        #The future state
        #The future mask
        
        self.Agent.add_experience_to_batch(state, rewards, action, future_state, future_mask)
        self._reset_memory()
        
                    
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
        
    def get_state(self):
        """
        Return a numerical representation of the player's current state.

        The state consists of:
        - The player's x and y coordinates.
        - 7 binary values representing the player's inventory. They indicate if the player is holding:
          - Plate (if so, also include fish and potato counts in dish_dict)
          - Raw Fish or Cut Fish or Fried Fish
          - Raw Potato or Cut Potato or Fried Potato
        
        Returns:
            List[float]: The player's state.
        """
        
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

        
    
