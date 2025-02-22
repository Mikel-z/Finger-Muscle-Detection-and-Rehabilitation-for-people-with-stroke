import cv2
import pyrealsense2 as rs
import numpy as np
import mediapipe as mp
import pygame
from calculate_angle import calculate_angle
import time
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from load_melody_chart_4 import load_melody_chart_4
import json
import pandas as pd
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Initialize an empty list to store angles and timestamps
angles_data = []
flexion_data = []
extension_data = []

# Save the extension_data and flexion_data lists to text files
def save_data_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

class DepthCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(config)

        # Create an align object
        self.align = rs.align(rs.stream.color)

        # Get the depth sensor's depth scale
        self.depth_scale = self.pipeline.get_active_profile().get_device().first_depth_sensor().get_depth_scale()

        # Get the intrinsics of the depth stream
        self.depth_intrinsics = self.pipeline.get_active_profile().get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
 
    def get_frame(self):
        try:
            frames = self.pipeline.wait_for_frames(10000)  # Increase timeout to 10000 milliseconds (10 seconds)
            aligned_frames = self.align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not depth_frame or not color_frame:
                return False, None, None
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            return True, depth_image, color_image
        except RuntimeError as e:
            print(f"Error fetching frames: {e}")
            return False, None, None

    def stop(self):
        self.pipeline.stop()

    def process_landmark(self, landmark_id, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values):
        # Ensure the coordinates are within the frame boundaries
        if 0 <= cx < frame_width and 0 <= cy < frame_height:
            depth_value = depth_frame[cy, cx] * self.depth_scale  # Convert depth value to meters
            z_values[landmark_id] = depth_value
            print(f"Landmark {landmark_id}: Depth value at ({cx}, {cy}) is {depth_value} meters")

            # Convert pixel coordinates to real-world coordinates
            real_world_coords = rs.rs2_deproject_pixel_to_point(self.depth_intrinsics, [cx, cy], depth_value)
            print(f"Landmark {landmark_id}: Real-world coordinates are {real_world_coords}")
            return real_world_coords
        else:
            print(f"Landmark {landmark_id}: Coordinates ({cx}, {cy}) are out of frame boundaries")
            return [0,0,0]

# Initialize Camera Intel Realsense
dc = DepthCamera()

# Initialize MediaPipe Hand
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PRESSED_COLOR = (128, 128, 128)  # Color when button is pressed

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("4-Key Musical Game")

# Load music file
pygame.mixer.music.load(r'C:\Users\zhuqi\Desktop\Thesis\music\1499092623.ogg')

def save_notes_to_file(notes, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for note in notes:
            file.write(f"{note[0]},{note[1]},{note[2]}\n")

# save note file
output_file_path = r'C:\Users\zhuqi\Desktop\Thesis\chart/notes_1.txt'
notes = load_melody_chart_4(r'C:\Users\zhuqi\Desktop\Thesis\chart\file.sm')
save_notes_to_file(notes, output_file_path)

# Define the Key class
class Key():
    def __init__(self, x, y, width,height, key):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.key = key
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = self.get_color()
        self.handled = False

    def get_color(self):
        if self.key == pygame.K_1:
            return RED
        elif self.key == pygame.K_2:
            return GREEN
        elif self.key == pygame.K_3:
            return BLUE
        elif self.key == pygame.K_4:
            return YELLOW

    def draw(self, screen, pressed):
        color = PRESSED_COLOR if pressed else self.color
        pygame.draw.rect(screen, color, self.rect)

def press_key_start(key_1):
    #print("start")
    if key_1 not in pressed_keys:
        pressed_keys.append(key_1)
        print(pressed_keys)
    
def press_key_end(key_2):
    #print("end")
    if key_2 in pressed_keys:
        pressed_keys.remove(key_2)
        print(pressed_keys)

# Button positions and dimensions
button_width = SCREEN_WIDTH // 4
button_height = 50
keys = [
    Key(0, SCREEN_HEIGHT - button_height, button_width, button_height, pygame.K_1),
    Key(button_width, SCREEN_HEIGHT - button_height, button_width, button_height, pygame.K_2),
    Key(2 * button_width, SCREEN_HEIGHT - button_height, button_width, button_height, pygame.K_3),
    Key(3 * button_width, SCREEN_HEIGHT - button_height, button_width, button_height, pygame.K_4)
]

# Start playing music
pygame.mixer.music.play()

# Function to display the accuracy as an end screen
def display_accuracy(accuracy):
    # Create a new window
    end_window = tk.Toplevel()
    end_window.title("Game Over")
    end_window.geometry("800x600")

    # Load the ending image
    ending_image = Image.open('images/ending_image.jpg')
    resized_ending_image = ending_image.resize((800, 600), Image.LANCZOS)
    ending_photo = ImageTk.PhotoImage(resized_ending_image)

    # Draw the text on the image
    draw = ImageDraw.Draw(resized_ending_image)
    font = ImageFont.truetype("arial.ttf", 24)  # Ensure you have the font file available
    text = f"Congratulations! Your accuracy is {accuracy:.2f}%"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (resized_ending_image.width - text_width) / 2
    text_y = (resized_ending_image.height - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill="white")

    # Convert the image to PhotoImage
    ending_photo = ImageTk.PhotoImage(resized_ending_image)

    # Create a label to display the image
    image_label = tk.Label(end_window, image=ending_photo)
    image_label.image = ending_photo  # Keep a reference to avoid garbage collection
    image_label.pack(fill=tk.BOTH, expand=True)

    # Run the window's main loop
    end_window.mainloop()

# Simulate game ending
def end_game(accuracy):
    # Display the accuracy
    display_accuracy(accuracy)

# Game loop
running = True
clock = pygame.time.Clock()
note_speed = 500
score = 0
note_index = 0
total_notes = len(notes)
hit_notes = 0
missed_notes = 0
accuracy = 0

pressed_keys = []

while running:

    screen.fill((0, 0, 0))
    ret, depth_frame, color_frame = dc.get_frame()
    if not ret:
        continue

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    
    # Normalize depth frame
    depth_frame_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
    depth_frame_normalized = np.uint8(depth_frame_normalized)

    # Normalize height and width based on depth frame dimensions
    height_frame_normalized = cv2.normalize(np.arange(depth_frame.shape[0]), None, 0, 255, cv2.NORM_MINMAX)
    height_frame_normalized = np.uint8(height_frame_normalized)

    width_frame_normalized = cv2.normalize(np.arange(depth_frame.shape[1]), None, 0, 255, cv2.NORM_MINMAX)
    width_frame_normalized = np.uint8(width_frame_normalized)
    

    # Process the color frame with MediaPipe
    color_frame_rgb = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(color_frame_rgb)

    # Get current time in the music
    current_time = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
    #print(f"Current time: {current_time}")
    
    k = pygame.key.get_pressed()
    # Update key.color1 and key.color2 for each key in keys
    for key in keys:
        key.color1 = (100, 100, 100)  # Example color for unpressed state
        key.color2 = (200, 200, 200)  # Example color for pressed state
    # Draw buttons
    # Reset the handled attribute for each button 
    for key in keys:
        if k[key.key] or key.key in pressed_keys:
            pygame.draw.rect(screen, key.color2, key.rect)
            key.handled = False
        else:
            pygame.draw.rect(screen, key.color1, key.rect)
            key.handled = True

    # Draw notes
    for note in notes[note_index:]:
        note_time, key, char = note
        #print(f"Note time: {note_time}, Key: {key}, Char: {char}")
        if note_time < current_time:
            note_index += 1
            continue
        y_pos = SCREEN_HEIGHT - (note_time - current_time) * note_speed
        #print(f"Drawing note at y_pos: {y_pos}")
        if y_pos < 0:
            break
        note_rect = pygame.Rect(key * button_width, int(y_pos), button_width, button_height)
        pygame.draw.rect(screen, WHITE, note_rect)
        
        # Check for key presses and collision
        for key in keys:
            if note_rect.colliderect(key.rect) and not key.handled:
                #print(f"Note hit: time_stamp={note_time}, key={key}")
                notes.remove(note)
                score += 100  # Increment score for hitting the note
                hit_notes += 1
                key.handled = True

            # Calculate accuracy
            if total_notes > 0:
                accuracy = (hit_notes / total_notes) * 100
            else:
                accuracy = 0

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks: 
            x_values = []
            y_values = []
            z_values = [None] * 21
            
            # Initialize x, y, z values
            x0 = x1 = x2 = x3 = x4 = x5 = x6 = x7 = x8 = x9 = x10 = x11 = x12 = x13 = x14 = x15 = x16 = x17 = x18 = x19 = x20 = 0
            y0 = y1 = y2 = y3 = y4 = y5 = y6 = y7 = y8 = y9 = y10 = y11 = y12 = y13 = y14 = y15 = y16 = y17 = y18 = y19 = y20 = 0
            z0 = z1 = z2 = z3 = z4 = z5 = z6 = z7 = z8 = z9 = z10 = z11 = z12 = z13 = z14 = z15 = z16 = z17 = z18 = z19 = z20 = 0

            #initialize landmarks
            Wrist = Thumb_CMC = Thumb_MCP = Thumb_IP = Thumb_TIP = Index_MCP = Index_PIP = Index_DIP = Index_TIP = Middle_MCP = Middle_PIP = Middle_DIP = Middle_TIP = Ring_MCP = Ring_PIP = Ring_DIP = Ring_TIP = Pinky_MCP = Pinky_PIP = Pinky_DIP = Pinky_TIP = [0, 0, 0]

            # Get frame dimensions
            frame_height, frame_width = depth_frame.shape   

            for id, lm in enumerate(handLms.landmark):
                h, w, c = color_frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                # Print the landmark coordinates
                #print(f'Landmark {id+1}: x={cx}, y={cy}, z={lm.z}')
                # Draw the landmark number next to the landmark
                cv2.putText(color_frame, str(id+1), (cx+5, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            #initialize x,y,z values

                if id == 0:
                    Wrist = dc.process_landmark(0, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)

                if id == 1:
                    Thumb_CMC = dc.process_landmark(1, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 2:
                    Thumb_MCP = dc.process_landmark(2, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 3:
                    Thumb_IP = dc.process_landmark(3, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 4:
                    Thumb_TIP = dc.process_landmark(4, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 5:
                    Index_MCP = dc.process_landmark(5, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                    #print(f'Index_MCP: {Index_MCP}')
                                    
                if id == 6:
                    Index_PIP = dc.process_landmark(6, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                    #print(f'Index_PIP: {Index_PIP}')
                
                if id == 7:
                    Index_DIP = dc.process_landmark(7, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                    #print(f'Index_DIP: {Index_DIP}')
                
                if id == 8:
                    Index_TIP = dc.process_landmark(8, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 9:
                    Middle_MCP = dc.process_landmark(9, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 10:
                    Middle_PIP = dc.process_landmark(10, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 11:
                    Middle_DIP = dc.process_landmark(11, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 12:
                    Middle_TIP = dc.process_landmark(12, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 13:
                    Ring_MCP = dc.process_landmark(13, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 14:
                    Ring_PIP = dc.process_landmark(14, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 15:
                    Ring_DIP = dc.process_landmark(15, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 16:
                    Ring_TIP = dc.process_landmark(16, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 17:
                    Pinky_MCP = dc.process_landmark(17, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 18:
                    Pinky_PIP = dc.process_landmark(18, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 19:
                    Pinky_DIP = dc.process_landmark(19, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 20:
                    Pinky_TIP = dc.process_landmark(20, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)

            # Filter out None values before performing the comparison
            valid_z_values = [z for z in z_values if z is not None]

            if all(0 < z < 1000 for z in valid_z_values) and all(0 <= x for x in x_values) and all(0 <= y for y in y_values):
                # Initialize all extension and flexion variables
                Thumb_MCP_extension = Thumb_MCP_flexion = 0
                Thumb_IP_extension = Thumb_IP_flexion = 0
                Index_MCP_extension = Index_MCP_flexion = 0
                Index_PIP_extension = Index_PIP_flexion = 0
                Index_DIP_extension = Index_DIP_flexion = 0
                Middle_MCP_extension = Middle_MCP_flexion = 0
                Middle_PIP_extension = Middle_PIP_flexion = 0
                Middle_DIP_extension = Middle_DIP_flexion = 0
                Ring_MCP_extension = Ring_MCP_flexion = 0
                Ring_PIP_extension = Ring_PIP_flexion = 0
                Ring_DIP_extension = Ring_DIP_flexion = 0
                Pinky_MCP_extension = Pinky_MCP_flexion = 0
                Pinky_PIP_extension = Pinky_PIP_flexion = 0
                Pinky_DIP_extension = Pinky_DIP_flexion = 0

                Thumb_MCP_angle = calculate_angle(Thumb_CMC, Thumb_MCP, Thumb_IP)
                #print(f"Thumb_MCP: {Thumb_MCP_angle} degrees")
                if Thumb_IP[2] > Thumb_MCP[2]:
                    Thumb_MCP_extension = Thumb_MCP_angle
                else:
                    Thumb_MCP_flexion = Thumb_MCP_angle

                Thumb_IP_angle = calculate_angle(Thumb_MCP, Thumb_IP, Thumb_TIP)
                #print(f"Thumb_IP: {Thumb_IP_angle} degrees")
                if Thumb_TIP[2] > Thumb_IP[2]:
                    Thumb_IP_extension = Thumb_IP_angle
                else:
                    Thumb_IP_flexion = Thumb_IP_angle
                    
                Index_MCP_angle = calculate_angle(Wrist, Index_MCP, Index_PIP)
                #print(f"Index_MCP: {Index_MCP_angle} degrees")
                if Index_PIP[2] > Index_MCP[2]:
                    Index_MCP_extension = Index_MCP_angle
                else:
                    Index_MCP_flexion = Index_MCP_angle

                Index_PIP_angle = calculate_angle(Index_MCP, Index_PIP, Index_DIP)
                #print(f"Index_PIP: {Index_PIP_angle} degrees")
                if Index_DIP[2] > Index_PIP[2]:
                    Index_PIP_extension = Index_PIP_angle
                else:
                    Index_PIP_flexion = Index_PIP_angle

                Index_DIP_angle = calculate_angle(Index_PIP, Index_DIP, Index_TIP)
                #print(f"Index_DIP: {Index_DIP_angle} degrees")
                if Index_TIP[2] > Index_DIP[2]:
                    Index_DIP_extension = Index_DIP_angle
                else:
                    Index_DIP_flexion = Index_DIP_angle

                Middle_MCP_angle = calculate_angle(Wrist, Middle_MCP, Middle_PIP)
                #print(f"Middle_MCP: {Middle_MCP_angle} degrees")
                if Middle_PIP[2] > Middle_MCP[2]:
                    Middle_MCP_extension = Middle_MCP_angle
                else:
                    Middle_MCP_flexion = Middle_MCP_angle

                Middle_PIP_angle = calculate_angle(Middle_MCP, Middle_PIP, Middle_DIP)
                #print(f"Middle_PIP: {Middle_PIP_angle} degrees")
                if Middle_DIP[2] > Middle_PIP[2]:
                    Middle_PIP_extension = Middle_PIP_angle
                else:
                    Middle_PIP_flexion = Middle_PIP_angle

                Middle_DIP_angle = calculate_angle(Middle_PIP, Middle_DIP, Middle_TIP)
                #print(f"Middle_DIP: {Middle_DIP_angle} degrees")
                if Middle_TIP[2] > Middle_DIP[2]:
                    Middle_DIP_extension = Middle_DIP_angle
                else:
                    Middle_DIP_flexion = Middle_DIP_angle

                Ring_MCP_angle = calculate_angle(Wrist, Ring_MCP, Ring_PIP)
                #print(f"Ring_MCP: {Ring_MCP_angle} degrees")
                if Ring_PIP[2] > Ring_MCP[2]:
                    Ring_MCP_extension = Ring_MCP_angle
                else:
                    Ring_MCP_flexion = Ring_MCP_angle

                Ring_PIP_angle = calculate_angle(Ring_MCP, Ring_PIP, Ring_DIP)
                #print(f"Ring_PIP: {Ring_PIP_angle} degrees")
                if Ring_DIP[2] > Ring_PIP[2]:
                    Ring_PIP_extension = Ring_PIP_angle
                else:
                    Ring_PIP_flexion = Ring_PIP_angle

                Ring_DIP_angle = calculate_angle(Ring_PIP, Ring_DIP, Ring_TIP)
                #print(f"Ring_DIP: {Ring_DIP_angle} degrees")
                if Ring_TIP[2] > Ring_DIP[2]:
                    Ring_DIP_extension = Ring_DIP_angle
                else:
                    Ring_DIP_flexion = Ring_DIP_angle

                Pinky_MCP_angle = calculate_angle(Wrist, Pinky_MCP, Pinky_PIP)
                #print(f"Pinky_MCP: {Pinky_MCP_angle} degrees")
                if Pinky_PIP[2] > Pinky_MCP[2]:
                    Pinky_MCP_extension = Pinky_MCP_angle
                else:
                    Pinky_MCP_flexion = Pinky_MCP_angle

                Pinky_PIP_angle = calculate_angle(Pinky_MCP, Pinky_PIP, Pinky_DIP)
                #print(f"Pinky_PIP: {Pinky_PIP_angle} degrees")
                if Pinky_DIP[2] > Pinky_PIP[2]:
                    Pinky_PIP_extension = Pinky_PIP_angle
                else:
                    Pinky_PIP_flexion = Pinky_PIP_angle

                Pinky_DIP_angle = calculate_angle(Pinky_PIP, Pinky_DIP, Pinky_TIP)
                #print(f"Pinky_DIP: {Pinky_DIP_angle} degrees")
                if Pinky_TIP[2] > Pinky_DIP[2]:
                    Pinky_DIP_extension = Pinky_DIP_angle
                else:
                    Pinky_DIP_flexion = Pinky_DIP_angle
                        
                # Capture the current timestamp
                timestamp = time.time()
                
                # Append the angles and timestamp to the list
                angles_data.append({
                    'timestamp': timestamp,
                    'Thumb_MCP_angle': Thumb_MCP_angle,
                    'Thumb_IP_angle': Thumb_IP_angle,
                    'Index_MCP_angle': Index_MCP_angle,
                    'Index_PIP_angle': Index_PIP_angle,
                    'Index_DIP_angle': Index_DIP_angle,
                    'Middle_MCP_angle': Middle_MCP_angle,
                    'Middle_PIP_angle': Middle_PIP_angle,
                    'Middle_DIP_angle': Middle_DIP_angle,
                    'Ring_MCP_angle': Ring_MCP_angle,
                    'Ring_PIP_angle': Ring_PIP_angle,
                    'Ring_DIP_angle': Ring_DIP_angle,
                    'Pinky_MCP_angle': Pinky_MCP_angle,
                    'Pinky_PIP_angle': Pinky_PIP_angle,
                    'Pinky_DIP_angle': Pinky_DIP_angle
                })

                extension_data.append({
                    'timestamp': timestamp,
                    'Thumb_MCP_extension': Thumb_MCP_extension,
                    'Thumb_IP_extension': Thumb_IP_extension,
                    'Index_MCP_extension': Index_MCP_extension,
                    'Index_PIP_extension': Index_PIP_extension,
                    'Index_DIP_extension': Index_DIP_extension,
                    'Middle_MCP_extension': Middle_MCP_extension,
                    'Middle_PIP_extension': Middle_PIP_extension,
                    'Middle_DIP_extension': Middle_DIP_extension,
                    'Ring_MCP_extension': Ring_MCP_extension,
                    'Ring_PIP_extension': Ring_PIP_extension,
                    'Ring_DIP_extension': Ring_DIP_extension,
                    'Pinky_MCP_extension': Pinky_MCP_extension,
                    'Pinky_PIP_extension': Pinky_PIP_extension,
                    'Pinky_DIP_extension': Pinky_DIP_extension
                })

                flexion_data.append({
                    'timestamp': timestamp,
                    'Thumb_MCP_flexion': Thumb_MCP_flexion,
                    'Thumb_IP_flexion': Thumb_IP_flexion,
                    'Index_MCP_flexion': Index_MCP_flexion,
                    'Index_PIP_flexion': Index_PIP_flexion,
                    'Index_DIP_flexion': Index_DIP_flexion,
                    'Middle_MCP_flexion': Middle_MCP_flexion,
                    'Middle_PIP_flexion': Middle_PIP_flexion,
                    'Middle_DIP_flexion': Middle_DIP_flexion,
                    'Ring_MCP_flexion': Ring_MCP_flexion,
                    'Ring_PIP_flexion': Ring_PIP_flexion,
                    'Ring_DIP_flexion': Ring_DIP_flexion,
                    'Pinky_MCP_flexion': Pinky_MCP_flexion,
                    'Pinky_PIP_flexion': Pinky_PIP_flexion,
                    'Pinky_DIP_flexion': Pinky_DIP_flexion
                })
            
                # Map angles to keys
                if Thumb_MCP_flexion > 15:
                    press_key_start(pygame.K_1)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, keys=pygame.K_1))
                else:
                    press_key_end(pygame.K_1)
                if Index_MCP_flexion > 15:  # Define threshold
                    press_key_start(pygame.K_2)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, keys=pygame.K_2))
                else:
                    press_key_end(pygame.K_2)
                if Middle_MCP_flexion > 15:
                    press_key_start(pygame.K_3)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, keys=pygame.K_3))
                else:
                    press_key_end(pygame.K_3)
                if Ring_MCP_flexion > 15:
                    press_key_start(pygame.K_4)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, keys=pygame.K_4))
                else:
                    press_key_end(pygame.K_4)

                # Compare z values and map space key
                if Middle_TIP[2] > Middle_MCP[2]:
                    press_key_start(pygame.K_SPACE)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, keys=pygame.K_SPACE))
                    #print('space')
                else:
                    press_key_end(pygame.K_SPACE)
            else:
                print("Some values are out of the valid range")

    # Display score and accuracy
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    accuracy_text = font.render(f"Accuracy: {accuracy:.2f}%", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(accuracy_text, (10, 50))

    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

    cv2.imshow("Color frame", color_frame)
    cv2.imshow("Depth frame", depth_frame_normalized)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
dc.stop()
cv2.destroyAllWindows()
pygame.quit()
end_game(accuracy)

# After the loop, extract angles and timestamps
timestamps = [data['timestamp'] for data in angles_data]
thumb_mcp_angles = [data['Thumb_MCP_angle'] for data in angles_data]
thumb_ip_angles = [data['Thumb_IP_angle'] for data in angles_data]
index_mcp_angles = [data['Index_MCP_angle'] for data in angles_data]
index_pip_angles = [data['Index_PIP_angle'] for data in angles_data]
index_dip_angles = [data['Index_DIP_angle'] for data in angles_data]
middle_mcp_angles = [data['Middle_MCP_angle'] for data in angles_data]
middle_pip_angles = [data['Middle_PIP_angle'] for data in angles_data]
middle_dip_angles = [data['Middle_DIP_angle'] for data in angles_data]
ring_mcp_angles = [data['Ring_MCP_angle'] for data in angles_data]
ring_pip_angles = [data['Ring_PIP_angle'] for data in angles_data]
ring_dip_angles = [data['Ring_DIP_angle'] for data in angles_data]
pinky_mcp_angles = [data['Pinky_MCP_angle'] for data in angles_data]
pinky_pip_angles = [data['Pinky_PIP_angle'] for data in angles_data]
pinky_dip_angles = [data['Pinky_DIP_angle'] for data in angles_data]

# Normalize timestamps to start from 0
start_time = timestamps[0]
normalized_timestamps = [t - start_time for t in timestamps]

# Assuming extension_data and flexion_data are already populated
# Extract angles and timestamps for extension
extension_timestamps = [data['timestamp'] for data in extension_data]
thumb_mcp_extension_angles = [data['Thumb_MCP_extension'] for data in extension_data]
thumb_ip_extension_angles = [data['Thumb_IP_extension'] for data in extension_data]
index_mcp_extension_angles = [data['Index_MCP_extension'] for data in extension_data]
index_pip_extension_angles = [data['Index_PIP_extension'] for data in extension_data]
index_dip_extension_angles = [data['Index_DIP_extension'] for data in extension_data]
middle_mcp_extension_angles = [data['Middle_MCP_extension'] for data in extension_data]
middle_pip_extension_angles = [data['Middle_PIP_extension'] for data in extension_data]
middle_dip_extension_angles = [data['Middle_DIP_extension'] for data in extension_data]
ring_mcp_extension_angles = [data['Ring_MCP_extension'] for data in extension_data]
ring_pip_extension_angles = [data['Ring_PIP_extension'] for data in extension_data]
ring_dip_extension_angles = [data['Ring_DIP_extension'] for data in extension_data]
pinky_mcp_extension_angles = [data['Pinky_MCP_extension'] for data in extension_data]
pinky_pip_extension_angles = [data['Pinky_PIP_extension'] for data in extension_data]
pinky_dip_extension_angles = [data['Pinky_DIP_extension'] for data in extension_data]

# Extract angles and timestamps for flexion
flexion_timestamps = [data['timestamp'] for data in flexion_data]
thumb_mcp_flexion_angles = [data['Thumb_MCP_flexion'] for data in flexion_data]
thumb_ip_flexion_angles = [data['Thumb_IP_flexion'] for data in flexion_data]
index_mcp_flexion_angles = [data['Index_MCP_flexion'] for data in flexion_data]
index_pip_flexion_angles = [data['Index_PIP_flexion'] for data in flexion_data]
index_dip_flexion_angles = [data['Index_DIP_flexion'] for data in flexion_data]
middle_mcp_flexion_angles = [data['Middle_MCP_flexion'] for data in flexion_data]
middle_pip_flexion_angles = [data['Middle_PIP_flexion'] for data in flexion_data]
middle_dip_flexion_angles = [data['Middle_DIP_flexion'] for data in flexion_data]
ring_mcp_flexion_angles = [data['Ring_MCP_flexion'] for data in flexion_data]
ring_pip_flexion_angles = [data['Ring_PIP_flexion'] for data in flexion_data]
ring_dip_flexion_angles = [data['Ring_DIP_flexion'] for data in flexion_data]
pinky_mcp_flexion_angles = [data['Pinky_MCP_flexion'] for data in flexion_data]
pinky_pip_flexion_angles = [data['Pinky_PIP_flexion'] for data in flexion_data]
pinky_dip_flexion_angles = [data['Pinky_DIP_flexion'] for data in flexion_data]

# Normalize timestamps to start from 0
start_time_extension = extension_timestamps[0]
normalized_extension_timestamps = [t - start_time_extension for t in extension_timestamps]

start_time_flexion = flexion_timestamps[0]
normalized_flexion_timestamps = [t - start_time_flexion for t in flexion_timestamps]

# Create the plot for extension angles
fig, ax = plt.subplots(figsize=(16, 8))
lines = []
lines.append(ax.plot(normalized_extension_timestamps, thumb_mcp_extension_angles, label='Thumb MCP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, thumb_ip_extension_angles, label='Thumb IP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, index_mcp_extension_angles, label='Index MCP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, index_pip_extension_angles, label='Index PIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, index_dip_extension_angles, label='Index DIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, middle_mcp_extension_angles, label='Middle MCP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, middle_pip_extension_angles, label='Middle PIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, middle_dip_extension_angles, label='Middle DIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, ring_mcp_extension_angles, label='Ring MCP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, ring_pip_extension_angles, label='Ring PIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, ring_dip_extension_angles, label='Ring DIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, pinky_mcp_extension_angles, label='Pinky MCP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, pinky_pip_extension_angles, label='Pinky PIP Extension')[0])
lines.append(ax.plot(normalized_extension_timestamps, pinky_dip_extension_angles, label='Pinky DIP Extension')[0])

plt.xlabel('Time (seconds)')
plt.ylabel('Angle (degrees)')
plt.title('Extension Angles Over Time')
plt.legend()

# Create checkboxes for toggling visibility
rax = plt.axes([0.9, 0.4, 0.1, 0.2], facecolor='lightgoldenrodyellow')
labels = [line.get_label() for line in lines]
visibility = [line.get_visible() for line in lines]
check = CheckButtons(rax, labels, visibility)

def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    plt.draw()

check.on_clicked(func)

# Save the plot
plt.savefig(r'C:\Users\zhuqi\Desktop\Thesis\extension_angles_plot.png')

plt.show()

# Create the plot for flexion angles
fig, ax = plt.subplots(figsize=(16, 8))
lines = []
lines.append(ax.plot(normalized_flexion_timestamps, thumb_mcp_flexion_angles, label='Thumb MCP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, thumb_ip_flexion_angles, label='Thumb IP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, index_mcp_flexion_angles, label='Index MCP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, index_pip_flexion_angles, label='Index PIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, index_dip_flexion_angles, label='Index DIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, middle_mcp_flexion_angles, label='Middle MCP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, middle_pip_flexion_angles, label='Middle PIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, middle_dip_flexion_angles, label='Middle DIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, ring_mcp_flexion_angles, label='Ring MCP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, ring_pip_flexion_angles, label='Ring PIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, ring_dip_flexion_angles, label='Ring DIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, pinky_mcp_flexion_angles, label='Pinky MCP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, pinky_pip_flexion_angles, label='Pinky PIP Flexion')[0])
lines.append(ax.plot(normalized_flexion_timestamps, pinky_dip_flexion_angles, label='Pinky DIP Flexion')[0])

plt.xlabel('Time (seconds)')
plt.ylabel('Angle (degrees)')
plt.title('Flexion Angles Over Time')
plt.legend()

# Create checkboxes for toggling visibility
rax = plt.axes([0.9, 0.4, 0.1, 0.2], facecolor='lightgoldenrodyellow')
labels = [line.get_label() for line in lines]
visibility = [line.get_visible() for line in lines]
check = CheckButtons(rax, labels, visibility)

def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    plt.draw()

check.on_clicked(func)

# Save the plot
plt.savefig(r'C:\Users\zhuqi\Desktop\Thesis\flexion_angles_plot.png')

plt.show()

# Define the file paths for text files
extension_data_txt_file = 'extension_data.txt'
flexion_data_txt_file = 'flexion_data.txt'

# Define the file paths for Excel files
extension_data_excel_file = 'extension_data_transposed.xlsx'
flexion_data_excel_file = 'flexion_data_transposed.xlsx'

# Save the data to text files
def save_data_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_data_to_file(extension_data, extension_data_txt_file)
save_data_to_file(flexion_data, flexion_data_txt_file)

# Convert lists to DataFrames
extension_df = pd.DataFrame(extension_data)
flexion_df = pd.DataFrame(flexion_data)

# Transpose the DataFrames to get the desired format
extension_df_transposed = extension_df.T
flexion_df_transposed = flexion_df.T

# Save transposed DataFrames to Excel files
extension_df_transposed.to_excel(extension_data_excel_file, header=False)
flexion_df_transposed.to_excel(flexion_data_excel_file, header=False)

# Print the transposed DataFrames for verification
print(extension_df_transposed)
print(flexion_df_transposed)