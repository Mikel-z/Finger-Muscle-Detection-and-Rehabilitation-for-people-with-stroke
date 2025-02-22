import cv2
import pyrealsense2 as rs
import numpy as np
import mediapipe as mp
import pygame
from calculate_angle import calculate_angle
import time
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from random import randint, choice
from sys import exit
# Initialize an empty list to store angles and timestamps
angles_data = []
flexion_data = []
extension_data = []

class DepthCamera:
    def __init__(self):
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(config)

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        self.align = rs.align(rs.stream.color)

    def get_frame(self):
        frames = self.pipeline.wait_for_frames()
        # Align the depth frame to color frame
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        if not depth_frame or not color_frame:
            return False, None, None
        return True, depth_image, color_image

    def release(self):
        self.pipeline.stop()
    
    # Function to locate landmarks coordinates and replace z value in mediapipehand with depth value from depth camera
    def process_landmark(id, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values):
        if 0 <= cy < frame_height and 0 <= cx < frame_width:
            z = depth_frame[cy, cx]
            x_values.append(cx)
            y_values.append(cy)
            z_values.append(z)
            #print(f'x{id}={cx}, y{id}={cy}, z{id}={z}')
            cv2.circle(color_frame, (cx, cy), 4, (0, 0, 255))
            cv2.putText(color_frame, "{}".format(z), (cx, cy - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            return [cx, cy, z]
        return [0, 0, 0]
    

# Initialize Camera Intel Realsense
dc = DepthCamera()

# Initialize MediaPipe Hand
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()


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


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
		player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
		self.player_walk = [player_walk_1,player_walk_2]
		self.player_index = 0
		self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()

		self.image = self.player_walk[self.player_index]
		self.rect = self.image.get_rect(midbottom = (80,300))
		self.gravity = 0

		self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
		self.jump_sound.set_volume(0.5)
 #if k[pygame.K_SPACE] or pygame.K_SPACE in pressed_keys
	def player_input(self):
		k = pygame.key.get_pressed()
		if k[pygame.K_SPACE] or pygame.K_SPACE in pressed_keys and self.rect.bottom >= 300:
			self.gravity = -20
			self.jump_sound.play()
               
	def apply_gravity(self):
		self.gravity += 1
		self.rect.y += self.gravity
		if self.rect.bottom >= 300:
			self.rect.bottom = 300

	def animation_state(self):
		if self.rect.bottom < 300: 
			self.image = self.player_jump
		else:
			self.player_index += 0.1
			if self.player_index >= len(self.player_walk):self.player_index = 0
			self.image = self.player_walk[int(self.player_index)]

	def update(self):
		self.player_input()
		self.apply_gravity()
		self.animation_state()

class Obstacle(pygame.sprite.Sprite):
	def __init__(self,type):
		super().__init__()
		
		if type == 'fly':
			fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
			fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
			self.frames = [fly_1,fly_2]
			y_pos = 210
		else:
			snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
			snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
			self.frames = [snail_1,snail_2]
			y_pos  = 300

		self.animation_index = 0
		self.image = self.frames[self.animation_index]
		self.rect = self.image.get_rect(midbottom = (randint(900,1100),y_pos))

	def animation_state(self):
		self.animation_index += 0.1 
		if self.animation_index >= len(self.frames): self.animation_index = 0
		self.image = self.frames[int(self.animation_index)]

	def update(self):
		self.animation_state()
		self.rect.x -= 6
		self.destroy()

	def destroy(self):
		if self.rect.x <= -100: 
			self.kill()

def display_score():
	current_time = int(pygame.time.get_ticks() / 1000) - start_time
	score_surf = test_font.render(f'Score: {current_time}',False,(64,64,64))
	score_rect = score_surf.get_rect(center = (400,50))
	screen.blit(score_surf,score_rect)
	return current_time

def collision_sprite():
	if pygame.sprite.spritecollide(player.sprite,obstacle_group,False):
		obstacle_group.empty()
		return False
	else: return True


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

pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0

# Load assets
#bg_music = pygame.mixer.Sound('audio/music.wav')
#bg_music.play(loops=-1)

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

sky_surface = pygame.image.load('graphics/Sky.png').convert()
ground_surface = pygame.image.load('graphics/ground.png').convert()

# Intro screen
player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))

game_name = test_font.render('Pixel Runner', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(400, 80))

game_message = test_font.render('Press space to run', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(400, 330))

running = True
game_active = False
score = 0
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 3000)



# Game loop
running = True
pressed_keys = []

while running:

    ret, depth_frame, color_frame = dc.get_frame()
    if not ret:
        continue


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


    k = pygame.key.get_pressed()
    # Update key.color1 and key.color2 for each key in keys

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))
        else:
            if k[pygame.K_SPACE] or pygame.K_SPACE in pressed_keys:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)

    if game_active:
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 300))
        score = display_score()

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        game_active = collision_sprite()
    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)

        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(400, 330))
        screen.blit(game_name, game_name_rect)

        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            screen.blit(score_message, score_message_rect)

	
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks: 
            x_values = []
            y_values = []
            z_values = []
            
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
                    Wrist = DepthCamera.process_landmark(0, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)

                if id == 1:
                    Thumb_CMC = DepthCamera.process_landmark(1, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 2:
                    Thumb_MCP = DepthCamera.process_landmark(2, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 3:
                    Thumb_IP = DepthCamera.process_landmark(3, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 4:
                    Thumb_TIP = DepthCamera.process_landmark(4, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 5:
                    Index_MCP = DepthCamera.process_landmark(5, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                    #print(f'Index_MCP: {Index_MCP}')
                                    
                if id == 6:
                    Index_PIP = DepthCamera.process_landmark(6, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                    #print(f'Index_PIP: {Index_PIP}')
                
                if id == 7:
                    Index_DIP = DepthCamera.process_landmark(7, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                    #print(f'Index_DIP: {Index_DIP}')
                
                if id == 8:
                    Index_TIP = DepthCamera.process_landmark(8, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 9:
                    Middle_MCP = DepthCamera.process_landmark(9, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 10:
                    Middle_PIP = DepthCamera.process_landmark(10, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 11:
                    Middle_DIP = DepthCamera.process_landmark(11, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 12:
                    Middle_TIP = DepthCamera.process_landmark(12, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 13:
                    Ring_MCP = DepthCamera.process_landmark(13, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 14:
                    Ring_PIP = DepthCamera.process_landmark(14, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 15:
                    Ring_DIP = DepthCamera.process_landmark(15, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 16:
                    Ring_TIP = DepthCamera.process_landmark(16, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 17:
                    Pinky_MCP = DepthCamera.process_landmark(17, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 18:
                    Pinky_PIP = DepthCamera.process_landmark(18, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 19:
                    Pinky_DIP = DepthCamera.process_landmark(19, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)
                
                if id == 20:
                    Pinky_TIP = DepthCamera.process_landmark(20, cx, cy, frame_height, frame_width, depth_frame, color_frame, z_values)

            if all(0 < z < 1000 for z in z_values) and all(0 <= x for x in x_values) and all(0 <= y for y in y_values):
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
                if Thumb_TIP[2] > Thumb_MCP[2]:
                    Thumb_MCP_extension = Thumb_MCP_angle
                else:
                    Thumb_MCP_flexion = Thumb_MCP_angle

                Thumb_IP_angle = calculate_angle(Thumb_MCP, Thumb_IP, Thumb_TIP)
                #print(f"Thumb_IP: {Thumb_IP_angle} degrees")
                if Thumb_TIP[2] > Thumb_MCP[2]:
                    Thumb_IP_extension = Thumb_IP_angle
                else:
                    Thumb_IP_flexion = Thumb_IP_angle
                    
                Index_MCP_angle = calculate_angle(Wrist, Index_MCP, Index_PIP)
                #print(f"Index_MCP: {Index_MCP_angle} degrees")
                if Index_TIP[2] > Index_MCP[2]:
                    Index_MCP_extension = Index_MCP_angle
                else:
                    Index_MCP_flexion = Index_MCP_angle

                Index_PIP_angle = calculate_angle(Index_MCP, Index_PIP, Index_DIP)
                #print(f"Index_PIP: {Index_PIP_angle} degrees")
                if Index_TIP[2] > Index_MCP[2]:
                    Index_PIP_extension = Index_PIP_angle
                else:
                    Index_PIP_flexion = Index_PIP_angle

                Index_DIP_angle = calculate_angle(Index_PIP, Index_DIP, Index_TIP)
                #print(f"Index_DIP: {Index_DIP_angle} degrees")
                if Index_TIP[2] > Index_MCP[2]:
                    Index_DIP_extension = Index_DIP_angle
                else:
                    Index_DIP_flexion = Index_DIP_angle

                Middle_MCP_angle = calculate_angle(Wrist, Middle_MCP, Middle_PIP)
                #print(f"Middle_MCP: {Middle_MCP_angle} degrees")
                if Middle_TIP[2] > Middle_MCP[2]:
                    Middle_MCP_extension = Middle_MCP_angle
                else:
                    Middle_MCP_flexion = Middle_MCP_angle

                Middle_PIP_angle = calculate_angle(Middle_MCP, Middle_PIP, Middle_DIP)
                #print(f"Middle_PIP: {Middle_PIP_angle} degrees")
                if Middle_TIP[2] > Middle_MCP[2]:
                    Middle_PIP_extension = Middle_PIP_angle
                else:
                    Middle_PIP_flexion = Middle_PIP_angle

                Middle_DIP_angle = calculate_angle(Middle_PIP, Middle_DIP, Middle_TIP)
                #print(f"Middle_DIP: {Middle_DIP_angle} degrees")
                if Middle_TIP[2] > Middle_MCP[2]:
                    Middle_DIP_extension = Middle_DIP_angle
                else:
                    Middle_DIP_flexion = Middle_DIP_angle

                Ring_MCP_angle = calculate_angle(Wrist, Ring_MCP, Ring_PIP)
                #print(f"Ring_MCP: {Ring_MCP_angle} degrees")
                if Ring_TIP[2] > Ring_MCP[2]:
                    Ring_MCP_extension = Ring_MCP_angle
                else:
                    Ring_MCP_flexion = Ring_MCP_angle

                Ring_PIP_angle = calculate_angle(Ring_MCP, Ring_PIP, Ring_DIP)
                #print(f"Ring_PIP: {Ring_PIP_angle} degrees")
                if Ring_TIP[2] > Ring_MCP[2]:
                    Ring_PIP_extension = Ring_PIP_angle
                else:
                    Ring_PIP_flexion = Ring_PIP_angle

                Ring_DIP_angle = calculate_angle(Ring_PIP, Ring_DIP, Ring_TIP)
                #print(f"Ring_DIP: {Ring_DIP_angle} degrees")
                if Ring_TIP[2] > Ring_MCP[2]:
                    Ring_DIP_extension = Ring_DIP_angle
                else:
                    Ring_DIP_flexion = Ring_DIP_angle

                Pinky_MCP_angle = calculate_angle(Wrist, Pinky_MCP, Pinky_PIP)
                #print(f"Pinky_MCP: {Pinky_MCP_angle} degrees")
                if Pinky_TIP[2] > Pinky_MCP[2]:
                    Pinky_MCP_extension = Pinky_MCP_angle
                else:
                    Pinky_MCP_flexion = Pinky_MCP_angle

                Pinky_PIP_angle = calculate_angle(Pinky_MCP, Pinky_PIP, Pinky_DIP)
                #print(f"Pinky_PIP: {Pinky_PIP_angle} degrees")
                if Pinky_TIP[2] > Pinky_MCP[2]:
                    Pinky_PIP_extension = Pinky_PIP_angle
                else:
                    Pinky_PIP_flexion = Pinky_PIP_angle

                Pinky_DIP_angle = calculate_angle(Pinky_PIP, Pinky_DIP, Pinky_TIP)
                #print(f"Pinky_DIP: {Pinky_DIP_angle} degrees")
                if Pinky_TIP[2] > Pinky_MCP[2]:
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
            
   
                # Compare z values and map space key
                if Middle_TIP[2] > Middle_MCP[2]:
                    press_key_start(pygame.K_SPACE)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, keys=pygame.K_SPACE))
                    #print('space')
                else:
                    press_key_end(pygame.K_SPACE)
            else:
                print("Some values are out of the valid range")

    # Update the display
    pygame.display.update()

    # Update display
    pygame.display.update()
    
    # Cap the frame rate
    clock.tick(60)

    cv2.imshow("Color frame", color_frame)
    cv2.imshow("Depth frame", depth_frame_normalized)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
dc.release()
cv2.destroyAllWindows()
pygame.quit()


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
