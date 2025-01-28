from Foods import Fish, Potato, Plate, MenuClass, ResourceGroup
from Objects import Fryer, CBoard, Floor
from Player import Player1, Player2
import numpy as np
import pygame
import tensorflow as tf

class Board:
    def __init__(self, map_generator):
        self.screen = pygame.display.set_mode((800, 600))
        self.Menu = MenuClass()
        self.StaticObjects = pygame.sprite.Group()
        self.Interactables = pygame.sprite.Group()
        self.NonPassables = pygame.sprite.Group()
        self.Players = pygame.sprite.Group()
        self.Resources = ResourceGroup()
        self.is_game_over = False
        #Get Interactables, NonPassables and Players, too
        
        floor_plan_matrix, idx2obj, coords2px, self.corner_coordinates, player1_coords, player2_coords = map_generator()
        for i in range (len(floor_plan_matrix)):
            for j in range (len(floor_plan_matrix[0])):     
                obj_class = idx2obj(floor_plan_matrix[i][j])     
                x, y = coords2px(j, i)
                object = obj_class(position=[x, y], board=self) 
                self.StaticObjects.add(object)
                if (object.is_nonpassable()):
                    self.NonPassables.add(object)
                
                if (object.is_interactable()):
                    self.Interactables.add(object)
        
        self.Player1 = Player1(coords2px(player1_coords[1], player1_coords[0]), self)
        self.Players.add(self.Player1)
        self.Player2 = Player2(coords2px(player2_coords[1], player2_coords[0]), self)
        self.Players.add(self.Player2)

        
    def draw(self):
        self.screen.fill((255, 255, 255)) 
        self.StaticObjects.draw(self.screen)
        self.Players.draw(self.screen)
        self.Menu.draw(self.screen, self.corner_coordinates)
        self.Resources.draw(self.screen)
        for interactable in self.Interactables:
            interactable.draw_progress_bar(self.screen)
        
        if self.is_game_over:
            self._draw_game_over()
            #Game finished; display a large "GAME OVER" sign over a frozen frame
    
    def _draw_game_over(self):
        START_X, START_Y, END_X, END_Y   = self.corner_coordinates
        
        font = pygame.font.SysFont("comicsansms", 100)
        game_over_surface = font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=((START_X+END_X)//2, (START_Y + END_Y)//2))
        
        score_text = f"Final Score: {self.Menu.game_score}"
        score_surface = font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(center=((START_X + END_X) // 2, (START_Y + END_Y) // 2 + 100))
        
        self.screen.blit(game_over_surface, game_over_rect)
        self.screen.blit(score_surface, score_rect)
    
    def game_over(self):
        #SET GAME_OVER AS TRUE, ADD DRAWING GAME_OVER TO SELF.DRAW()
        self.is_game_over = True
    
    def update(self, keys):
        if not self.is_game_over:
            self.Interactables.update()
            self.Players.update(keys=keys, board=self) 
            self.Menu.update()
            self.draw()
        
        else:
            self._draw_game_over()
    
    def _get_visual_data(self):
        visual_data = pygame.surfarray.array3d(self.screen)
        visual_data = np.transpose(visual_data, (1, 0, 2)) #Change from width, height, color channel to height, width, color channel
        start_x, start_y, end_x, end_y = self.corner_coordinates
        
        visual_data = visual_data[start_y - self.Menu.height: end_y, start_x:end_x]
        visual_data = visual_data / 255. #Normalize pixels from 0 to 1 for easier training
        visual_data = np.expand_dims(visual_data, axis=0)
        
        visual_data_tensor = tf.convert_to_tensor(visual_data, dtype=tf.float32)
        
        new_size = (108, 144)
        return tf.image.resize(visual_data_tensor, new_size, method='bilinear')
    
    def _get_numerical_data(self):
        numerical_data = self.Menu.get_state()
        for Player in self.Players:
            numerical_data.extend(Player.get_state())
            
        return tf.convert_to_tensor([numerical_data]) #Add a batch dimension

    
    def get_state(self):
        '''
        Returns the list of:
        - visual_data - normalized pixel values of the screen
        - numerical_data, containing in respective order:
            - the state of the Menu (see: Menu.get_state())
            - the state of Player 1's and Player 2's hands (see: Player.get_state())
        
        '''
        
        visual_data = self._get_visual_data()
        numerical_data = self._get_numerical_data()
        
        return [visual_data, numerical_data]
    
    
    def _get_ingredient_rewards(self, ingredient, raw_coeff, prep_coeff):
        reward = raw_coeff
        if ingredient.chopped:
            reward += prep_coeff
        
        if ingredient.fried:
            reward += prep_coeff
            
        if isinstance(ingredient.place, Fryer) or isinstance(ingredient.place, CBoard):
            reward += 0.25 * prep_coeff
        
        if (ingredient.progress != 0):
            reward += 0.75 * prep_coeff * ingredient.progress/100
        
        return reward
        

    def get_rewards(self):
        '''
        Computes the total amount of rewards for the current game state. 
        Rewards = game score * 10
        Additionally:
        Raw food needed to finish the menu is worth 50 points, 
        Cut food on the menu - 150 points 
        Fried food on the menu - 250 points
        Plate - 500 points
        '''
        
        raw_coeff = 50
        prep_coeff = 150
        plate_coeff = 50
        
        rewards = self.Menu.game_score*10
        
        fish_points = []
        potato_points = []
        plate_points = []
        
        foods = []
        for Interactable in self.Interactables:
            if(Interactable.resource != None):
                foods.append(Interactable.resource) 
        
        for Player in self.Players:
            if(Player.hands != None):
                foods.append(Player.hands)
        
        for food in foods:
            if isinstance(food, Plate):
                plate_points.append(plate_coeff)
                for ingredient in food.dish:
                    reward = self._get_ingredient_rewards(ingredient, raw_coeff, prep_coeff)
                    if isinstance(ingredient, Fish):
                        fish_points.append(reward)
                    
                    if isinstance(ingredient, Potato):
                        potato_points.append(reward)
            
            else:
                reward = self._get_ingredient_rewards(food, raw_coeff, prep_coeff)
                if isinstance(food, Fish):
                    fish_points.append(reward)
                
                if isinstance(food, Potato):
                    potato_points.append(reward)
                    
        fish_on_menu = sum([dish.ingredients_dict["Fish"] for dish in self.Menu.queue])
        potato_on_menu = sum([dish.ingredients_dict["Potato"] for dish in self.Menu.queue])
        plate_on_menu = len(self.Menu.queue)
        
        fish_points.sort(reverse = True)
        potato_points.sort(reverse = True)
        plate_points.sort(reverse = True)
            
        rewards += sum(fish_points[:fish_on_menu])
        rewards += sum(potato_points[:potato_on_menu])
        rewards += sum(plate_points[:plate_on_menu])
        
        return float(rewards)

    def draw_q_value_heatmap(self, agent, update=True):
        """
        Draws a heatmap of Q-values overlaid on the game board for the current state.
        
        Args:
            agent: The Agent object used to evaluate Q-values
            update: If True, recalculates the heatmap. If False, displays the last calculated heatmap.
        """
        if update:
            # Store original player position
            original_pos = self.Player1.rect.center
            
            # Create empty heatmap matching floor plan dimensions
            floor_positions = []
            max_x = max_y = 0
            min_x = min_y = float('inf')
            
            # Find valid floor positions and heatmap dimensions
            for obj in self.StaticObjects:
                if isinstance(obj, Floor):
                    x, y = obj.rect.center
                    floor_positions.append((x, y))
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
            
            # Calculate grid dimensions
            width = int((max_x - min_x) / 32) + 1  # Using 32px tile width
            height = int((max_y - min_y) / 32) + 1  # Using 32px tile height
            heatmap = np.zeros((height, width))
            
            # Test each floor position
            for pos in floor_positions:
                # Move player to test position
                self.Player1.rect.center = pos
                self.draw()
                
                # Get state and Q-values
                visual_state = self._get_visual_data()
                numerical_state = self._get_numerical_data()
                q_values = agent.get_qs([visual_state, numerical_state])
                max_q = np.max(q_values)
                
                # Convert position to grid coordinates
                grid_x = int((pos[0] - min_x) / 32)
                grid_y = int((pos[1] - min_y) / 32)
                heatmap[grid_y, grid_x] = max_q
            
            # Restore original position
            self.Player1.rect.center = original_pos
            self.draw()
            
            # Normalize heatmap for visualization
            non_zero_mask = heatmap != 0
            if non_zero_mask.any():
                min_val = np.min(heatmap[non_zero_mask])
                max_val = np.max(heatmap[non_zero_mask])
                if max_val - min_val != 0:
                    normalized = np.zeros_like(heatmap)
                    normalized[non_zero_mask] = (heatmap[non_zero_mask] - min_val) / (max_val - min_val)
                else:
                    normalized = heatmap
            else:
                normalized = heatmap

            # Store the calculated values for future use
            self._last_heatmap = heatmap
            self._last_normalized = normalized
            self._last_min_x = min_x
            self._last_min_y = min_y
        else:
            # Use stored values from last calculation
            if not hasattr(self, '_last_heatmap'):
                return  # No previous heatmap to display
            heatmap = self._last_heatmap
            normalized = self._last_normalized
            min_x = self._last_min_x
            min_y = self._last_min_y
        
        # Draw heatmap overlay
        cell_width = cell_height = 32
        font = pygame.font.Font(None, 20)
        
        for y in range(normalized.shape[0]):
            for x in range(normalized.shape[1]):
                value = normalized[y, x]
                if value > 0:  # Only draw cells with Q-values
                    # Create color gradient from blue (low) to red (high)
                    scaled_value = value ** 2  # Square the value to emphasize high values
                    color = (int(255 * scaled_value), 0, int(255 * (1-scaled_value)), 128)
                    rect = pygame.Rect(
                        x * cell_width + min_x, 
                        y * cell_height + min_y,
                        cell_width,
                        cell_height
                    )
                    pygame.draw.rect(self.screen, color, rect)
                    
                    # Add Q-value text
                    q_value = heatmap[y, x]
                    text = font.render(f"{q_value:.2f}", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(
                        x * cell_width + min_x + cell_width//2, 
                        y * cell_height + min_y + cell_height//2
                    ))
                    self.screen.blit(text, text_rect)
        
        # Draw legend
        legend_surface = pygame.Surface((150, 80), pygame.SRCALPHA)
        pygame.draw.rect(legend_surface, (0, 0, 0, 180), legend_surface.get_rect())
        
        # Create gradient rectangle
        gradient_rect = pygame.Surface((100, 20))
        for x in range(100):
            scaled_x = (x/100) ** 2
            color = (int(255 * scaled_x), 0, int(255 * (1-scaled_value)), 200)
            pygame.draw.line(gradient_rect, color, (x, 0), (x, 20))
        
        # Add legend text
        font = pygame.font.Font(None, 24)
        title = font.render("Q-Values", True, (255, 255, 255))
        low = font.render("Low", True, (255, 255, 255))
        high = font.render("High", True, (255, 255, 255))
        
        # Position legend elements
        legend_surface.blit(title, (10, 5))
        legend_surface.blit(gradient_rect, (25, 30))
        legend_surface.blit(low, (5, 55))
        legend_surface.blit(high, (100, 55))
        
        # Position legend in top-right corner
        self.screen.blit(legend_surface, (630, 20))
        
        pygame.display.flip()