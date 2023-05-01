import os
import openai
from map_parser import GameMap
import time
import json

# Load API Key from file
with open('api_key.txt', 'r') as file:
    openai.api_key = file.read().replace('\n', '')

MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.2

game_map = GameMap()
game_map.initialize()

COLOR_MAPPING = {
    '.': '\033[30m.\033[0m', # black
    'W': '\033[44mW\033[0m', # blue background
    '#': '\033[47m#\033[0m', # white background
    'P': '\033[90mP\033[0m', # gray
    'C': '\033[33mC\033[0m' # yellow
}

context = [{'role':'system', 'content':"""
You can ONLY answer questions in the following JSON format outlined in curly brackets:
{
"inner-thoughts": "<thoughts>",
"movement": "<movement direction>"
}
the movement key should only be either UP, DOWN, LEFT, RIGHT, or NONE

C represents your position in the world
P represents a path
# represents a wall

Your goal is to follow the path
"""}]


def get_completion_from_messages(messages, model=MODEL, temperature=TEMPERATURE):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]

def append_to_context(message):
    context.append(message)
    while sum(len(msg['content']) for msg in context) > 8192:
        context.pop(0)

def get_response(prompt):
    append_to_context({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context)
    validate_and_append_response(response)
    return response

def validate_and_append_response(response):
    try:
        json.loads(response)
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response}")
        response = '{}'
    append_to_context({'role':'assistant', 'content':f"{response}"})

def color_map(map):
    return ''.join(COLOR_MAPPING.get(character, character) for character in map)

def print_game_info(colored_map, extra_information, movement_direction, extra_thoughts):
    print("Map: ")
    print(colored_map)
    print("\n")
    print("Extra Information: ", extra_information)
    print("\n")
    print("----------[ CHARACTER ]----------")
    print("Moving: ", movement_direction)
    print("Thinking About: ", extra_thoughts)
    print("\n")
    print(f"Currently at: {game_map.pos_x, game_map.pos_y}")
    print(f"Currently standing on: {game_map.standing_on()}")
    print(sum(len(msg['content']) for msg in context))

def game_loop():
    output = f"""
    {{
    "map": ".PPP#......\\nPPP.#######\\nPPP.......W\\nPP.......WW\\nP........WW\\n.....C..WWW\\n.......WWWW\\n......WWWW#\\n......WWWW#\\n......WWWW#\\n......WWWW#",
    "extra-information": "None"
    }}
    """
    while True:
        output_dict = json.loads(output)
        map = output_dict.get("map").replace('\\n', '\n')
        extra_information = output_dict.get("extra-information")

        if map.lower() == "quit":
            break

        response = get_response(map)

        response_dict = json.loads(response)
        movement_direction = response_dict.get("movement")
        extra_thoughts = response_dict.get("inner-thoughts")

        colored_map = color_map(map)

        os.system('cls')
        print_game_info(colored_map, extra_information, movement_direction, extra_thoughts)

        output = game_map.move_c(movement_direction, True)
        time.sleep(0.5)

if __name__ == '__main__':
    game_loop()