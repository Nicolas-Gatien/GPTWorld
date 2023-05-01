from PIL import Image
import json

class GameMap:
    def __init__(self):
        self.map = ""
        self.grid = []
        self.width = 0
        self.height = 0
        self.pos_x = None
        self.pos_y = None
        self.prev_char = None
        self.last_movement = None
        self.initialize()

    def initialize(self):
        self.map = self.construct_map().strip()
        lines = self.map.split('\n')
        self.grid = [list(line) for line in lines]
        self.height = len(self.grid)
        self.width = len(self.grid[0])  # Assuming all lines have the same width
        self.pos_x, self.pos_y = None, None
        self.prev_char = None
        self.find_c()

    def construct_map(self):
        img = Image.open("map.png")
        pixels = img.load()
        color_map = {
            (219, 229, 69, 255): '.',
            (0, 0, 0, 255): '#',
            (45, 164, 215, 255): 'W',
            (144, 124, 104, 255): 'P',
            (0, 0, 255, 255): 'C'
        }
        ascii_lines = []
        for j in range(img.size[1]):  # height
            line = ""
            for i in range(img.size[0]):  # width
                rgb = pixels[i, j]
                char = color_map.get(rgb, ' ')
                line += char
            ascii_lines.append(line)

        return "\n".join(ascii_lines)

    def get_subgrid(self, width, height, x, y):
        half_size = 7  # Half of the 11x11 sub-grid size
        subgrid = ""
        for j in range(max(0, y - half_size), min(height, y + half_size + 1)):
            for i in range(max(0, x - half_size), min(width, x + half_size + 1)):
                subgrid += self.grid[j][i]
            subgrid += "\n"
        return subgrid

    def find_c(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 'C':
                    self.pos_x, self.pos_y = x, y
                    self.prev_char = '.'  # Assuming 'C' initially replaced a space character
                    return self.get_subgrid(self.width, self.height, x, y)

        return "C not found in the grid"

    def move_c(self, direction, recurse):
        dx, dy = 0, 0
        on_path = False
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
        
        new_x, new_y = self.pos_x + dx, self.pos_y + dy
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height or self.grid[new_y][new_x] == '#':
            return json.dumps({
                "map": self.get_subgrid(self.width, self.height, self.pos_x, self.pos_y).replace('\n', '\\n'),
                "extra-information": "Can't move in that direction",
                "standing-on": self.standing_on(),
                "last-movement": self.last_movement if self.last_movement else "None"
            })
        
        # Restore the previous character at the old position
        self.grid[self.pos_y][self.pos_x] = self.prev_char

        # Store the character at the new position
        self.prev_char = self.grid[new_y][new_x]

        # Move 'C' to the new position
        self.grid[new_y][new_x] = 'C'
        self.pos_x, self.pos_y = new_x, new_y

        if (self.standing_on() == "PATH"):
                    on_path = True
        if (on_path and recurse is True):
            self.move_c(direction, False)

        return json.dumps({
            "map": self.get_subgrid(self.width, self.height, self.pos_x, self.pos_y).replace('\n', '\\n'),
            "extra-information": "None",
            "standing-on": self.standing_on(),
            "last-movement": self.last_movement if self.last_movement else "None"
        })

    def standing_on(self):
        if self.prev_char == '.':
            return "GROUND"
        elif self.prev_char == 'W':
            return "WATER"
        elif self.prev_char == 'P':
            return "PATH"