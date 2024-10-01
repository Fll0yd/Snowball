import logging
import threading
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from snake.snake import game_loop  # Adjusted import
from core.config_loader import load_config

# Load game preferences from game_preferences.json
game_prefs = load_config('game_preferences.json')

def start_snake_game():
    snake_settings = game_prefs['snake']
    speed = snake_settings['speed']
    grid_size = snake_settings['grid_size']
    
    # Use these settings in the game logic
    print(f"Starting Snake with speed {speed} and grid size {grid_size}.")

class GameInterface:
    def __init__(self):
        self.games = {
            'snake': self.launch_snake,
            'billiards': self.launch_billiards,
            'asteroids': self.launch_asteroids,
            'pacman': self.launch_pacman,
            'minesweeper': self.launch_minesweeper,
            'dino': self.launch_dino_game,
            '2048': self.launch_2048,
            'chess': self.launch_chess,
            'hill_climb_racing': self.launch_hill_climb_racing,
            'pong': self.launch_pong,
            'rubiks_cube': self.launch_rubiks_cube,
            'flappy_bird': self.launch_flappy_bird,
            'piano_tiles': self.launch_piano_tiles,
            'tetris': self.launch_tetris,
            'connect_4': self.launch_connect_4,
            'clicker_heroes': self.launch_clicker_heroes,
            'jump_king': self.launch_jump_king,
            'walk': self.launch_walk,
            'creature_creator': self.launch_creature_creator,
            'drive': self.launch_drive,
            'fly': self.launch_fly,
            'donkey_kong': self.launch_donkey_kong,
            'guitar_hero': self.launch_guitar_hero,
            'suika_game': self.launch_suika_game,
            'risk': self.launch_risk,
        }
        self.active_game = None
        self.logger = logging.getLogger("SnowballAI.GameInterface")
        self.logger.info("Game Interface initialized.")

    def list_available_games(self):
        """List all available games."""
        return list(self.games.keys())

    def launch_game(self, game_name):
        """Launch the selected game."""
        game_name = game_name.lower()
        if game_name in self.games:
            try:
                self.logger.info(f"Launching game: {game_name}")
                self.games[game_name]()
            except Exception as e:
                self.logger.error(f"Error launching {game_name}: {str(e)}")
        else:
            self.logger.warning(f"Game '{game_name}' is not available.")
            print(f"Game '{game_name}' is not available.")

    def run_game_in_thread(self, game_func):
        """Run the game in a separate thread to avoid blocking."""
        game_thread = threading.Thread(target=game_func)
        game_thread.start()

    # Placeholder for each game launch function
    def launch_snake(self):
        """Launch Snake game."""
        from games.snake.snake import game_loop
        game_loop()

    def launch_billiards(self):
        """Launch Billiards game."""
        print("Launching Billiards game...")
        # Add actual game launch logic here

    def launch_asteroids(self):
        """Launch Asteroids game."""
        print("Launching Asteroids game...")
        # Add actual game launch logic here

    def launch_minesweeper(self):
        """Launch Minesweeper game."""
        print("Launching Minesweeper game...")
        # Add actual game launch logic here

    def launch_dino_game(self):
        """Launch Google Chrome Dinosaur game."""
        print("Launching Dino game...")
        # Add actual game launch logic here

    def launch_2048(self):
        """Launch 2048 game."""
        print("Launching 2048 game...")
        # Add actual game launch logic here

    def launch_chess(self):
        """Launch Chess game."""
        print("Launching Chess game...")
        # Add actual game launch logic here

    def launch_hill_climb_racing(self):
        """Launch Hill Climb Racing game."""
        print("Launching Hill Climb Racing game...")
        # Add actual game launch logic here

    def launch_pong(self):
        """Launch Pong game."""
        print("Launching Pong game...")
        # Add actual game launch logic here

    def launch_rubiks_cube(self):
        """Launch Rubik's Cube game."""
        print("Launching Rubik's Cube game...")
        # Add actual game launch logic here

    def launch_flappy_bird(self):
        """Launch Flappy Bird game."""
        print("Launching Flappy Bird game...")
        # Add actual game launch logic here

    def launch_piano_tiles(self):
        """Launch Piano Tiles game."""
        print("Launching Piano Tiles game...")
        # Add actual game launch logic here

    def launch_tetris(self):
        """Launch Tetris game."""
        print("Launching Tetris game...")
        # Add actual game launch logic here

    def launch_connect_4(self):
        """Launch Connect 4 game."""
        print("Launching Connect 4 game...")
        # Add actual game launch logic here

    def launch_clicker_heroes(self):
        """Launch Clicker Heroes game."""
        print("Launching Clicker Heroes game...")
        # Add actual game launch logic here

    def launch_jump_king(self):
        """Launch Jump King game."""
        print("Launching Jump King game...")
        # Add actual game launch logic here

    def launch_walk(self):
        """Launch Walk game."""
        print("Launching Walk game...")
        # Add actual game launch logic here

    def launch_creature_creator(self):
        """Launch Creature Creator game."""
        print("Launching Creature Creator game...")
        # Add actual game launch logic here

    def launch_drive(self):
        """Launch Drive game."""
        print("Launching Drive game...")
        # Add actual game launch logic here

    def launch_fly(self):
        """Launch Fly game."""
        print("Launching Fly game...")
        # Add actual game launch logic here

    def launch_donkey_kong(self):
        """Launch Donkey Kong game."""
        print("Launching Donkey Kong game...")
        # Add actual game launch logic here

    def launch_guitar_hero(self):
        """Launch Guitar Hero game."""
        print("Launching Guitar Hero game...")
        # Add actual game launch logic here

    def launch_suika_game(self):
        """Launch Suika Game."""
        print("Launching Suika Game...")
        # Add actual game launch logic here

    def launch_risk(self):
        """Launch RISK game."""
        print("Launching RISK game...")
        # Add actual game launch logic here

    def launch_pacman(self):
        """Launch PacMan game."""
        print("Launching PacMan game...")
        # Add actual game launch logic here

    def start_game(self, game_name):
        """Start a specified game by name."""
        game_name = game_name.lower()
        if game_name in self.games:
            self.logger.info(f"Starting {game_name} game.")
            self.active_game = game_name
            self.launch_game(game_name)
        else:
            self.logger.warning(f"Game '{game_name}' not found.")
            print(f"Game '{game_name}' not found.")

    def stop_game(self):
        """Stop the current active game."""
        if self.active_game:
            self.logger.info(f"Stopping {self.active_game} game.")
            # Implement game-specific stop logic if needed
            print(f"{self.active_game.capitalize()} game stopped.")
            self.active_game = None
        else:
            self.logger.info("No active game to stop.")
            print("No active game is currently running.")

    def get_active_game(self):
        """Return the name of the currently active game."""
        return self.active_game if self.active_game else "No active game."

# Example usage
if __name__ == "__main__":
    game_interface = GameInterface()
    print(game_interface.list_available_games())  # List available games
    game_interface.start_game("snake")  # Start Snake game