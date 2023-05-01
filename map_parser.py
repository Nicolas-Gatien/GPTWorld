from PIL import Image
import os
import time
import random
from colorama import Fore, Style
import json

map = ""

# Split into lines and convert into 2D grid
lines = map.split('\n')
grid = [list(line) for line in lines]

# Define other global variables
height = len(grid)
width = len(grid[0])  # Assuming all lines have the same width
pos_x, pos_y = None, None
prev_char = None
last_movement = None

def initialize():
    global map, grid, height, width, pos_x, pos_y, prev_char
    map = construct_map().strip()

    # Split into lines and convert into 2D grid
    lines = map.split('\n')
    grid = [list(line) for line in lines]

    # Define other global variables
    height = len(grid)
    width = len(grid[0])  # Assuming all lines have the same width
    pos_x, pos_y = None, None
    prev_char = None

    find_c()

def construct_map():
    # load the image
    img = Image.open("map.png")
    pixels = img.load()

    # define the RGB values and corresponding characters to use
    color_map = {
        (219, 229, 69, 255): '.',
        (0, 0, 0, 255): '#',
        (45, 164, 215, 255): 'W',
        (144, 124, 104, 255): 'P',
        (0, 0, 255, 255): 'C'
    }

    # iterate through each pixel and map to a character
    ascii_lines = []
    for j in range(img.size[1]): # height
        line = ""
        for i in range(img.size[0]): # width
            # get the RGB values of the current pixel
            rgb = pixels[i, j]
            # map the RGB values to a character based on the color map
            char = color_map.get(rgb, ' ')
            # append the character to the line
            line += char
        # append the line to the ASCII lines
        ascii_lines.append(line)

    map = ""

    # print the ASCII art
    for line in ascii_lines:
        map += line + "\n"
    
    return map
def get_subgrid(grid, width, height, x, y):
    half_size = 7  # Half of the 11x11 sub-grid size
    subgrid = ""
    
    for j in range(max(0, y - half_size), min(height, y + half_size + 1)):
        for i in range(max(0, x - half_size), min(width, x + half_size + 1)):
            subgrid += grid[j][i]
        subgrid += "\n"
        
    return subgrid
def find_c():
    global grid, width, height, pos_x, pos_y, prev_char
    for y in range(height):
        for x in range(width):
            if grid[y][x] == 'C':
                pos_x, pos_y = x, y
                prev_char = '.'  # Assuming 'C' initially replaced a space character
                return get_subgrid(grid, width, height, x, y)
                
    return "C not found in the grid"
def move_c(direction):
    global grid, pos_x, pos_y, width, height, prev_char, last_movement
    dx, dy = 0, 0
    
    if direction == "UP":
        dy = -1
    elif direction == "DOWN":
        dy = 1
    elif direction == "LEFT":
        dx = -1
    elif direction == "RIGHT":
        dx = 1
    elif direction == "NONE":
        pass
    else:
        return f"Invalid direction: {direction}"

    new_x, new_y = pos_x + dx, pos_y + dy

    # If the new position is out of the grid or is occupied by '#', don't move
    if new_x < 0 or new_x >= width or new_y < 0 or new_y >= height or grid[new_y][new_x] == '#':
        return json.dumps({
            "map": get_subgrid(grid, width, height, pos_x, pos_y).replace('\n', '\\n'),
            "extra-information": "Can't move in that direction",
            "standing-on": standing_on(),
            "last-movement": last_movement if last_movement else "None"
        })

    # Restore the previous character at the old position
    grid[pos_y][pos_x] = prev_char
    
    # Store the character at the new position
    prev_char = grid[new_y][new_x]

    # Move 'C' to the new position
    grid[new_y][new_x] = 'C'
    pos_x, pos_y = new_x, new_y

    # Return the new subgrid

    return json.dumps({
        "map": get_subgrid(grid, width, height, pos_x, pos_y).replace('\n', '\\n'),
        "extra-information": "None",
        "standing-on": standing_on(),
        "last-movement": last_movement if last_movement else "None"
    })
    
def standing_on():
    if prev_char == '.':
        return "GROUND"
    elif prev_char == 'W':
        return "WATER"
    elif prev_char == 'P':
        return "PATH"

'''while (True):   
    os.system('cls')
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    direction = random.choice(directions)
    print(move_c(direction))
    print(f"Currently at: {pos_x, pos_y}")
    print(f"Currently standing on: {standing_on()}")
    time.sleep(0.1)'''
