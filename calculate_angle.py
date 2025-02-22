import numpy as np

def calculate_angle(base, mcp, pip):
    # Convert points to numpy arrays
    base = np.array(base)
    mcp = np.array(mcp)
    pip = np.array(pip)
    
    # Calculate vectors
    v1 = mcp - base
    v2 = pip - mcp
    
    # Calculate the dot product
    dot_product = np.dot(v1, v2)

    # Calculate the magnitude of the vectors
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    
    # Calculate the angle in radians
    angle = np.arccos(dot_product / (magnitude_v1 * magnitude_v2))
    
    # Convert the angle to degrees
    angle_degrees = np.degrees(angle)
    
    return angle_degrees

# Function to map angles to music keys
'''
def map_angle_to_key(angle):
    if angle < 30:
        return 'C'
    elif angle < 60:
        return 'D'
    elif angle < 90:
        return 'E'
    else:
        return 'F'
'''
'''  
def map_angle_to_key(Index_PIP, Middle_PIP, Ring_PIP, Pinky_PIP):
    if angle < 30:
        return 'C'
    elif angle < 60:
        return 'D'
    elif angle < 90:
        return 'E'
    else:
        return 'F'
'''
'''
# Example usage with dummy coordinates
base = [0, 0, 0]  # Replace with actual coordinates
mcp = [1, 1, 0]   # Replace with actual coordinates
pip = [2, 0, 0]   # Replace with actual coordinates

angle = calculate_angle(base, mcp, pip)
print(f"Angle: {angle} degrees")
'''

#peppets
#holding the curvature and boxes 
#smaller and smaller spheres