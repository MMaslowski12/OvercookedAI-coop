import numpy as np
from Objects import Floor
from GameClass import Game
from Agent import Agent
import pygame

def generate_q_value_heatmap(player=1, normalized=True, use_max_q=True):
    """
    Generates a heatmap of Q-values by testing different player positions.
    Args:
        player: 1 for Player1, 2 for Player2
        normalized: Whether to normalize the Q-values
        use_max_q: If True, uses maximum Q-value. If False, uses Q-value for action 4
    Returns a numpy array of Q-values corresponding to floor positions.
    """
    Misha = Agent(learning=False, save_file="Misha"+str(player)+".keras") 
    GameObj = Game(misha_playing=True, tick_length=1000, models = [Misha, Misha], learning = False, debug = True, visual_debug = True)

    # Get player object based on parameter
    player_obj = GameObj.Board.Player1 if player == 1 else GameObj.Board.Player2

    # Store original player position
    original_pos = player_obj.rect.center
    
    # Create empty heatmap matching floor plan dimensions
    floor_positions = []
    max_x = max_y = 0
    min_x = min_y = float('inf')
    
    # Find valid floor positions and heatmap dimensions
    for obj in GameObj.Board.StaticObjects:
        if isinstance(obj, Floor):
            x, y = obj.rect.center
            floor_positions.append((x, y))
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
    
    # Calculate grid dimensions
    width = int((max_x - min_x) / 32) + 1  # Assuming 32px tile width
    height = int((max_y - min_y) / 32) + 1 # Assuming 32px tile height
    heatmap = np.zeros((height, width))
    
    # Test each floor position
    for pos in floor_positions:
        # Move player to test position
        player_obj.rect.center = pos
        GameObj.Board.draw()
        
        # Get state and Q-values
        visual_state = GameObj.Board._get_visual_data()
        numerical_state = GameObj.Board._get_numerical_data()
        q_values = Misha.get_qs([visual_state, numerical_state])
        q_value = np.max(q_values) if use_max_q else q_values[4]  # Use max Q or Q-value for action 4
        
        # Convert position to grid coordinates
        grid_x = int((pos[0] - min_x) / 32)
        grid_y = int((pos[1] - min_y) / 32)
        heatmap[grid_y, grid_x] = q_value
        
    # Restore original position
    player_obj.rect.center = original_pos
    
    # Normalize heatmap using mean and standard deviation
    non_zero_mask = heatmap != 0
    mean = None
    std = None
    if non_zero_mask.any():
        non_zero_values = heatmap[non_zero_mask]
        mean = np.mean(non_zero_values)
        std = np.std(non_zero_values)
        if std != 0 and normalized:
            heatmap[non_zero_mask] = (heatmap[non_zero_mask] - mean) / std
    
    return heatmap, GameObj.Board, mean, std

print("xd?")
player = 1
# Generate heatmap for Player1 by default
heatmap, board, mean, std = generate_q_value_heatmap(player, normalized=False, use_max_q=False)

def display_heatmap(heatmap, board):
    # Create a surface for the heatmap
    heatmap_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    
    # Get dimensions
    height, width = heatmap.shape
    cell_width = cell_height = 32  # Match tile size used in generation
    
    # Normalize values to 0-1 range for coloring
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
        
    # First draw the board
    board.draw()
    screen = pygame.display.get_surface()
        
    # Draw each cell
    font = pygame.font.Font(None, 20)
    for y in range(height):
        for x in range(width):
            value = normalized[y, x]
            if value > 0:  # Only draw cells with Q-values
                # Create color gradient from blue (low) to red (high)
                # Use exponential scaling to make differences more pronounced
                scaled_value = value ** 2  # Square the value to emphasize high values
                color = (int(255 * scaled_value), 0, int(255 * (1-scaled_value)), 128)  # More transparent
                rect = pygame.Rect(
                    x * cell_width, 
                    y * cell_height,
                    cell_width,
                    cell_height
                )
                pygame.draw.rect(screen, color, rect)
                
                # Add Q-value text
                q_value = heatmap[y, x]
                text = font.render(f"{q_value:.2f}", True, (255, 255, 255))
                text_rect = text.get_rect(center=(x * cell_width + cell_width//2, 
                                                y * cell_height + cell_height//2))
                screen.blit(text, text_rect)
                
    # Create legend
    legend_surface = pygame.Surface((150, 100), pygame.SRCALPHA)  # Made taller to fit numbers
    pygame.draw.rect(legend_surface, (0, 0, 0, 180), legend_surface.get_rect())
    
    # Add min/max values
    min_val_text = font.render(f"{min_val:.2f}", True, (255, 255, 255))
    max_val_text = font.render(f"{max_val:.2f}", True, (255, 255, 255))
    legend_surface.blit(min_val_text, (5, 75))  # Below "Low"
    legend_surface.blit(max_val_text, (85, 75))  # Below "High"
    # Create gradient rectangle with exponential scaling
    gradient_rect = pygame.Surface((100, 20))
    for x in range(100):
        scaled_x = (x/100) ** 2  # Square the value like above
        color = (int(255 * scaled_x), 0, int(255 * (1-scaled_x)), 200)
        pygame.draw.line(gradient_rect, color, (x, 0), (x, 20))
    
    # Add text
    font = pygame.font.Font(None, 24)
    title = font.render("Q-Values", True, (255, 255, 255))
    low = font.render("Low", True, (255, 255, 255))
    high = font.render("High", True, (255, 255, 255))
    
    # Position elements
    legend_surface.blit(title, (10, 5))
    legend_surface.blit(gradient_rect, (25, 30))
    legend_surface.blit(low, (5, 55))
    legend_surface.blit(high, (100, 55))
    
    # Position legend in top-right corner
    screen.blit(legend_surface, (630, 20))
    
    pygame.display.flip()
    
print("xd?")
display_heatmap(heatmap, board)
print(mean, std)

# Wait for user to close window
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

pygame.quit()
