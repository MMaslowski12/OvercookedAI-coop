from .looper import Looper
import logging
import pygame
from .utils import keys2list
from .expert_system import ExpertSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.current_policy_name = None
        self.current_policy_args = None

    def set_params(self, board, player):
        self.board = board
        self.player = player

    def draw_policy_info(self, screen, pos):
        # pos is a tuple (x, y) specifying where to render the policy info on the screen.
        # This method uses pygame to render the current policy name and args.
        font = pygame.font.SysFont("Arial", 20)
        
        # Draw current policy at the top
        info_text = f"Policy: {self.current_policy_name}, args: {self.current_policy_args}"
        text_surface = font.render(info_text, True, (0, 0, 0))
        screen.blit(text_surface, pos)

    def action(self):
        pass

class HumanAgent(Agent):
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.current_policy_name = "Human Agent"
        self.current_policy_args = "None"
        super().__init__(board, player)

    def action(self):
        return keys2list(pygame.key.get_pressed(), self.player.controls)

class LEMAgent(Agent):
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.expert_system = ExpertSystem(player)
        self.looper = Looper(grammar_function=self.expert_system.grammar_function)
        super().__init__(board, player)

    def set_params(self, board, player):
        super().set_params(board, player)
        self.expert_system.player = player
        self.looper.set_player(player)

    def update(self):
        state = self.board.get_state()
        self.looper.update_agent(state)

    def draw_policy_info(self, screen, pos):
        # pos is a tuple (x, y) specifying where to render the policy info on the screen.
        # This method uses pygame to render the current policy name and args.
        font = pygame.font.SysFont("Arial", 20)
        
        # Draw current policy at the top
        info_text = f"Policy: {self.current_policy_name}, args: {self.current_policy_args}"
        text_surface = font.render(info_text, True, (0, 0, 0))
        screen.blit(text_surface, pos)
        
        # Draw policies in two rows with 5 policies per row
        policy_y1 = screen.get_height() - 80 + pos[1]  # First row position
        policy_y2 = screen.get_height() - 40 + pos[1]  # Second row position
        max_width = screen.get_width() - pos[0] - 20  # Maximum width available per row
        
        # Split policies into two rows
        policy_texts_row1 = []
        policy_texts_row2 = []
        
        for i, (policy_name, policy_args) in enumerate(self.looper.policy):
            policy_text = f"{i}: {policy_name}, {policy_args}"
            if i < 5:  # First 5 policies go to first row
                policy_texts_row1.append(policy_text)
            else:  # Remaining policies go to second row
                policy_texts_row2.append(policy_text)
        
        # Calculate total width needed for each row
        row1_width = 0
        row2_width = 0
        
        for text in policy_texts_row1:
            text_surface = font.render(text, True, (0, 0, 0))
            row1_width += text_surface.get_width() + 20
            
        for text in policy_texts_row2:
            text_surface = font.render(text, True, (0, 0, 0))
            row2_width += text_surface.get_width() + 20
        
        # Calculate appropriate font size for each row
        font_size1 = 20
        if row1_width > max_width and len(policy_texts_row1) > 0:
            scale_factor = max_width / row1_width
            font_size1 = max(int(20 * scale_factor), 8)
            
        font_size2 = 20
        if row2_width > max_width and len(policy_texts_row2) > 0:
            scale_factor = max_width / row2_width
            font_size2 = max(int(20 * scale_factor), 8)
        
        # Use the smaller of the two font sizes for consistency
        adjusted_font_size = min(font_size1, font_size2)
        adjusted_font = pygame.font.SysFont("Arial", adjusted_font_size)
        
        # Draw first row
        x_offset = 0
        for policy_text in policy_texts_row1:
            policy_surface = adjusted_font.render(policy_text, True, (0, 0, 0))
            screen.blit(policy_surface, (pos[0] + x_offset, policy_y1))
            x_offset += policy_surface.get_width() + 20
            
        # Draw second row
        x_offset = 0
        for policy_text in policy_texts_row2:
            policy_surface = adjusted_font.render(policy_text, True, (0, 0, 0))
            screen.blit(policy_surface, (pos[0] + x_offset, policy_y2))
            x_offset += policy_surface.get_width() + 20

    def action(self):
        self.update()
        policy_name, policy_args = self.looper.get_policy()
        self.current_policy_name = policy_name
        self.current_policy_args = policy_args

        actions, done = self.expert_system(policy_name, policy_args)

        if done:
            self.looper.new_policy()

        #TODO Later -- get this to an Agent so that it can update the list based on movements. Add feedback to the agent, too

        return actions
        