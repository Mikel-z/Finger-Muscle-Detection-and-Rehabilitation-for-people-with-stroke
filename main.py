import subprocess
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

def launch_game_1():
    subprocess.Popen(['python', 'mediapipehand_musical_game_3.py'])

def launch_game_2():
    subprocess.Popen(['python', 'mediapipehand_musical_game_2.py'])

def launch_game_3():
    subprocess.Popen(['python', 'mediapipehand_musical_game_1.py'])

def launch_game_4():
    subprocess.Popen(['python', 'mediapipehand_musical_game_4.py'])

def launch_game_5():
    subprocess.Popen(['python', 'mediapipehand_musical_game_5.py'])

# New function to launch the jump game
def launch_jump_game():
    subprocess.Popen(['python', 'mediapipehand_jump_game_2.py'])

# Create the main window
root = tk.Tk()
root.title("Game Launcher")
root.geometry("800x600")

# Load and set the background image
background_image = Image.open('images/background.jpg')
resized_background_image = background_image.resize((800, 600), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(resized_background_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# Create the title label
title_label = tk.Label(root, text="Finger Tracking Game", font=("Helvetica", 24), bg='black', fg='white')
title_label.pack(pady=20)

# Function to resize images
def resize_image(image_path, size):
    image = Image.open(image_path)
    resized_image = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(resized_image)

# Load and resize images for buttons
button_images = {
    'game_1': resize_image('images/game_1.png', (200, 40)),
    'game_2': resize_image('images/game_2.png', (200, 40)),
    'game_3': resize_image('images/game_3.png', (200, 40)),
    'game_4': resize_image('images/game_4.png', (200, 40)),
    'game_5': resize_image('images/game_5.png', (200, 40)),
    'runner_game': resize_image('images/jump_game.png', (200, 40))
}

# Custom font
custom_font = font.Font(family="Comic Sans MS", size=14, weight="bold")

# Create buttons with images and custom font
buttons = [
    {'text': 'Level 1 music', 'command': launch_game_1, 'image': button_images['game_1']},
    {'text': 'Level 2 music', 'command': launch_game_2, 'image': button_images['game_2']},
    {'text': 'Level 3 music', 'command': launch_game_3, 'image': button_images['game_3']},
    {'text': 'Level 4 music', 'command': launch_game_4, 'image': button_images['game_4']},
    {'text': 'Level 5 music', 'command': launch_game_5, 'image': button_images['game_5']},
    {'text': 'Runner', 'command': launch_jump_game, 'image': button_images['runner_game']}
]

for button in buttons:
    tk.Button(
        root,
        text=button['text'],
        command=button['command'],
        image=button['image'],
        compound=tk.CENTER,
        font=custom_font,
        bg='white',
        fg='black',
        activebackground='yellow',
        activeforeground='red',
        padx=10,
        pady=10
    ).pack(pady=10)

# Add a separator
separator = tk.Label(root, text="--------------------", font=("Helvetica", 16), bg='black', fg='white')
separator.pack(pady=10)

# Run the main loop
root.mainloop()