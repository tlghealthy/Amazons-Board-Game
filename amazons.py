"""
Amazons Prototype with Enhanced Separation Check and Flood Fill Move Count

This version includes:
- An updated are_all_units_separated() function that flood fills in all 8 directions.
- A new flood_fill_area() function (and helper for players) that counts the reachable spaces
  from each unit via 8-direction connectivity (through empty cells or cells with the same color).
- The remaining moves print-out now shows both queen-like moves and total flood fill area for each player.
- Winner detection and unit highlighting (selected unit is outlined in yellow).
"""

import pygame
import sys
import json

def load_settings(filename="settings.json"):
    """Load game settings from a JSON file."""
    with open(filename, "r") as f:
        settings = json.load(f)
    print("Settings loaded:", settings)
    return settings

def create_board(width, height):
    """Initialize the board as a 2D grid filled with 'empty' cells."""
    board = [["empty" for _ in range(width)] for _ in range(height)]
    print(f"Created board with dimensions {width}x{height}")
    return board

def place_initial_units(board, player_units):
    """Place player units on the board based on the positions specified in the settings."""
    for player, units in player_units.items():
        for pos in units:
            x, y = pos  # positions are given as [x, y]
            board[y][x] = player
            print(f"Placed {player} unit at ({x}, {y})")
    return board

def draw_board(screen, board, cell_size, selected_piece):
    """Draw the grid, player pieces, walls, and highlight the selected unit."""
    screen.fill((255, 255, 255))
    height = len(board)
    width = len(board[0])
    for y in range(height):
        for x in range(width):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            # Highlight the selected piece with a yellow border.
            if selected_piece is not None and (x, y) == selected_piece:
                pygame.draw.rect(screen, (255, 255, 0), rect, 3)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # grid lines
            if board[y][x] == "white":
                pygame.draw.circle(screen, (255, 255, 255), rect.center, cell_size // 2 - 4)
                pygame.draw.circle(screen, (0, 0, 0), rect.center, cell_size // 2 - 4, 2)
            elif board[y][x] == "black":
                pygame.draw.circle(screen, (0, 0, 0), rect.center, cell_size // 2 - 4)
            elif board[y][x] == "wall":
                pygame.draw.rect(screen, (128, 128, 128), rect)
    pygame.display.flip()

def is_valid_move(board, start, end):
    """
    Check if moving from start to end is valid.
    The move must be in a straight line (horizontal, vertical, or diagonal)
    with no pieces or walls in between and the destination cell must be empty.
    """
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy

    print(f"Validating move from {start} to {end} (dx: {dx}, dy: {dy})")

    if dx == 0 and dy == 0:
        print("Move is zero-length.")
        return False

    # Determine step increments
    if dx == 0:
        step_x = 0
        step_y = 1 if dy > 0 else -1
    elif dy == 0:
        step_y = 0
        step_x = 1 if dx > 0 else -1
    elif abs(dx) == abs(dy):
        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
    else:
        print("Move is not in a straight line.")
        return False

    # Check intermediate cells
    x, y = sx + step_x, sy + step_y
    while (x, y) != (ex, ey):
        if board[y][x] != "empty":
            print(f"Path blocked at ({x}, {y}) by '{board[y][x]}'")
            return False
        x += step_x
        y += step_y

    if board[ey][ex] != "empty":
        print(f"Destination ({ex}, {ey}) is not empty (found '{board[ey][ex]}').")
        return False

    print("Move is valid.")
    return True

def get_valid_moves_for_unit(board, pos):
    """
    Get a list of all valid queen-like moves for a unit at the given position.
    Moves follow queen-like (straight line) movement through empty cells.
    """
    directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]
    valid_moves = []
    x0, y0 = pos
    height = len(board)
    width = len(board[0])
    for dx, dy in directions:
        x, y = x0 + dx, y0 + dy
        while 0 <= x < width and 0 <= y < height and board[y][x] == "empty":
            valid_moves.append((x, y))
            x += dx
            y += dy
    return valid_moves

def count_valid_moves_for_player(board, player):
    """
    Count the total number of valid queen-like moves available for all units belonging to the player.
    """
    total_moves = 0
    height = len(board)
    width = len(board[0])
    for y in range(height):
        for x in range(width):
            if board[y][x] == player:
                moves = get_valid_moves_for_unit(board, (x, y))
                total_moves += len(moves)
    return total_moves

def are_all_units_separated(board):
    """
    Check if all units are separated by walls.
    For each unit, perform a flood fill (on the current board state) that expands
    through empty cells and cells containing the same color as the starting unit.
    The flood fill now expands in all 8 directions.
    If during the flood fill an opposing unit is encountered (adjacent in any of the 8 directions),
    the units are not fully separated.
    """
    height = len(board)
    width = len(board[0])
    # Use 8 directions for flood fill.
    directions = [(dx, dy) for dx in [-1,0,1] for dy in [-1,0,1] if not (dx == 0 and dy == 0)]
    
    for y in range(height):
        for x in range(width):
            if board[y][x] in ["white", "black"]:
                starting_color = board[y][x]
                stack = [(x, y)]
                visited = set()
                while stack:
                    cx, cy = stack.pop()
                    if (cx, cy) in visited:
                        continue
                    visited.add((cx, cy))
                    for dx, dy in directions:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if board[ny][nx] == "wall":
                                continue
                            # Allowed: empty or same color.
                            if board[ny][nx] == "empty" or board[ny][nx] == starting_color:
                                stack.append((nx, ny))
                            # If an opposing unit is encountered, they are connected.
                            elif board[ny][nx] != starting_color:
                                print(f"Flood fill from unit at {(x, y)} ({starting_color}) reached opposing unit at {(nx, ny)} ({board[ny][nx]})")
                                return False
    return True

def flood_fill_area(board, pos, color):
    """
    Compute the flood fill area starting from pos, using 8-direction connectivity.
    For flood fill, cells that are empty or occupied by the same color are considered reachable.
    We treat the starting cell as if it were empty (since the unit could move out).
    """
    height = len(board)
    width = len(board[0])
    directions = [(dx, dy) for dx in [-1,0,1] for dy in [-1,0,1] if not (dx == 0 and dy == 0)]
    stack = [pos]
    visited = set()
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                # Allow flood fill through empty cells or cells with the same color.
                if board[ny][nx] == "empty" or board[ny][nx] == color:
                    stack.append((nx, ny))
    return len(visited)

def count_flood_fill_area_for_player(board, player):
    """
    Sum the flood fill areas (using 8-direction connectivity) for each unit belonging to the player.
    """
    total_area = 0
    height = len(board)
    width = len(board[0])
    for y in range(height):
        for x in range(width):
            if board[y][x] == player:
                # Treat the unit's position as starting point.
                area = flood_fill_area(board, (x, y), player)
                total_area += area
    return total_area

def main():
    # Load settings
    settings = load_settings()
    board_width = settings.get("board_width", 20)
    board_height = settings.get("board_height", 20)
    cell_size = settings.get("cell_size", 30)
    player_units = settings.get("player_units", {
        "white": [[0, 7], [0, 12], [19, 7], [19, 12]],
        "black": [[7, 0], [12, 0], [7, 19], [12, 19]]
    })
    starting_player = settings.get("starting_player", "white")

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((board_width * cell_size, board_height * cell_size))
    pygame.display.set_caption("Amazons Prototype")
    board = create_board(board_width, board_height)
    board = place_initial_units(board, player_units)

    current_player = starting_player
    selected_piece = None
    # Game states: "select_piece" (choose a unit), "select_destination" (move the unit), "select_arrow" (shoot arrow)
    state = "select_piece"
    print(f"Starting game. Current player: {current_player}")

    running = True
    while running:
        draw_board(screen, board, cell_size, selected_piece)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event received.")
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                grid_x = mouse_pos[0] // cell_size
                grid_y = mouse_pos[1] // cell_size

                print(f"\nMouse click at pixel {mouse_pos}, grid position: ({grid_x}, {grid_y})")
                
                if grid_x < 0 or grid_x >= board_width or grid_y < 0 or grid_y >= board_height:
                    print("Click outside board bounds.")
                    continue

                if state == "select_piece":
                    print(f"State: select_piece | Clicked cell contains: '{board[grid_y][grid_x]}'")
                    if board[grid_y][grid_x] == current_player:
                        selected_piece = (grid_x, grid_y)
                        print(f"Selected {current_player} piece at {selected_piece}")
                        state = "select_destination"
                    else:
                        print("No valid piece at the clicked position.")
                elif state == "select_destination":
                    print(f"State: select_destination | Attempting to move from {selected_piece} to ({grid_x}, {grid_y})")
                    if is_valid_move(board, selected_piece, (grid_x, grid_y)):
                        sx, sy = selected_piece
                        board[sy][sx] = "empty"
                        board[grid_y][grid_x] = current_player
                        selected_piece = (grid_x, grid_y)
                        print(f"Moved piece to {selected_piece}")
                        state = "select_arrow"
                    else:
                        print("Invalid move destination.")
                elif state == "select_arrow":
                    print(f"State: select_arrow | Attempting arrow shot from {selected_piece} to ({grid_x}, {grid_y})")
                    if is_valid_move(board, selected_piece, (grid_x, grid_y)):
                        board[grid_y][grid_x] = "wall"
                        print(f"Arrow shot to ({grid_x}, {grid_y})")
                        selected_piece = None
                        state = "select_piece"
                        # Switch current player
                        current_player = "black" if current_player == "white" else "white"
                        print(f"Turn ended. Next player: {current_player}")
                        # Check if the new current player has any queen-like moves.
                        queen_moves = count_valid_moves_for_player(board, current_player)
                        print(f"{current_player} has {queen_moves} valid queen moves.")
                        if queen_moves == 0:
                            winner = "black" if current_player == "white" else "white"
                            print(f"No valid moves for {current_player}. {winner} wins!")
                            running = False
                        # Additionally, if all units are separated by walls, print flood fill areas.
                        if are_all_units_separated(board):
                            white_moves = count_valid_moves_for_player(board, "white")
                            black_moves = count_valid_moves_for_player(board, "black")
                            white_area = count_flood_fill_area_for_player(board, "white")
                            black_area = count_flood_fill_area_for_player(board, "black")
                            print("All units are separated by walls.")
                            print(f"Remaining moves - White: {white_moves} queen moves, {white_area} flood fill spaces")
                            print(f"Remaining moves - Black: {black_moves} queen moves, {black_area} flood fill spaces")
                    else:
                        print("Invalid arrow shot.")
        pygame.time.wait(50)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
