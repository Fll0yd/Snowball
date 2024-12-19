# game_interface.py (S:/Snowball/interface)
 
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import threading
import logging
import os
import sys

from Snowball.decom.OLDinitializer import SnowballInitializer

class GameInterface:
    def __init__(self, master, logger=None, config_loader=None, q_learning_agent=None):
        # Use initializer if logger, config_loader, or q_learning_agent are not provided
        initializer = SnowballInitializer() if not logger or not config_loader or not q_learning_agent else None
        self.logger = logger if logger else initializer.logger
        self.config_loader = config_loader if config_loader else initializer.config_loader
        self.q_learning_agent = q_learning_agent if q_learning_agent else initializer.q_learning_agent

        self.master = master
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
        self.logger.log_event("Game Interface initialized.")

        # Set up the game interface UI
        self.setup_game_interface()

    def setup_game_interface(self):
        """Set up the game interface with buttons for each game."""
        self.master.title("Snowball AI - Game Interface")
        self.master.geometry("1250x950")
        self.master.configure(bg="#2c2c2c")

        game_frame = tk.Frame(self.master, bg="#2c2c2c")
        game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        row = 0
        col = 0
        for game_name in self.games:
            image_path = os.path.join("S:/Snowball/icon/games", f"{game_name}.png")
            try:
                game_image = Image.open(image_path).resize((150, 150), Image.ANTIALIAS)
                game_photo = ImageTk.PhotoImage(game_image)
            except FileNotFoundError:
                self.logger.log_event(f"Game image not found for {game_name} at {image_path}")
                game_photo = None

            game_button = tk.Button(
                game_frame, text=game_name.capitalize(), image=game_photo, compound=tk.TOP,
                command=lambda name=game_name: self.launch_game(name),
                bg="#1e1e1e", fg="white", font=("Arial", 12, "bold"), relief="flat",
                activebackground="#3e3e3e", activeforeground="white", padx=10, pady=10
            )
            game_button.image = game_photo  # Keep a reference to avoid garbage collection
            game_button.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            col += 1
            if col > 3:  # Limit to 4 games per row
                col = 0
                row += 1

        # Configure grid weights for even spacing
        for i in range(4):
            game_frame.grid_columnconfigure(i, weight=1)
        for i in range((len(self.games) + 3) // 4):
            game_frame.grid_rowconfigure(i, weight=1)

    def launch_game(self, game_name):
        """Launch the selected game."""
        game_name = game_name.lower()
        if game_name in self.games:
            try:
                self.logger.log_event(f"Launching game: {game_name}")
                self.run_game_in_thread(self.games[game_name])  # Use threading for game
            except Exception as e:
                self.logger.log_event(f"Error launching {game_name}: {str(e)}")
        else:
            self.logger.log_event(f"Game '{game_name}' is not available.")

    def run_game_in_thread(self, game_func):
        """Run the game in a separate thread to avoid blocking."""
        def thread_wrapper():
            try:
                game_func()
            except Exception as e:
                self.logger.log_event(f"Error occurred in game thread: {e}")
                print(f"Error occurred in game thread: {e}")

        game_thread = threading.Thread(target=thread_wrapper)
        game_thread.daemon = True
        game_thread.start()

    # Game launch methods
    def launch_snake(self):
        from ..games.snake.snake import SnakeAI
        snake_ai = SnakeAI()
        snake_ai.game_loop()

    def launch_billiards(self):
        print("Launching Billiards game...")

    def launch_asteroids(self):
        print("Launching Asteroids game...")

    def launch_pacman(self):
        print("Launching PacMan game...")

    def launch_minesweeper(self):
        print("Launching Minesweeper game...")

    def launch_dino_game(self):
        print("Launching Dino game...")

    def launch_2048(self):
        print("Launching 2048 game...")

    def launch_chess(self):
        print("Launching Chess game...")

    def launch_hill_climb_racing(self):
        print("Launching Hill Climb Racing game...")

    def launch_pong(self):
        print("Launching Pong game...")

    def launch_rubiks_cube(self):
        print("Launching Rubik's Cube game...")

    def launch_flappy_bird(self):
        print("Launching Flappy Bird game...")

    def launch_piano_tiles(self):
        print("Launching Piano Tiles game...")

    def launch_tetris(self):
        print("Launching Tetris game...")

    def launch_connect_4(self):
        print("Launching Connect 4 game...")

    def launch_clicker_heroes(self):
        print("Launching Clicker Heroes game...")

    def launch_jump_king(self):
        print("Launching Jump King game...")

    def launch_walk(self):
        print("Launching Walk game...")

    def launch_creature_creator(self):
        print("Launching Creature Creator game...")

    def launch_drive(self):
        print("Launching Drive game...")

    def launch_fly(self):
        print("Launching Fly game...")

    def launch_donkey_kong(self):
        print("Launching Donkey Kong game...")

    def launch_guitar_hero(self):
        print("Launching Guitar Hero game...")

    def launch_suika_game(self):
        print("Launching Suika Game...")

    def launch_risk(self):
        print("Launching RISK game...")


if __name__ == "__main__":
    root = tk.Tk()
    initializer = SnowballInitializer()
    game_interface = GameInterface(root, initializer.logger, initializer.config_loader, initializer.q_learning_agent)
    root.mainloop()
