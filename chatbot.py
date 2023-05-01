import os
import openai
import map_parser as mp
import time
import json

openai.api_key = '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'

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.2):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]
def get_response(prompt):
    context.append({'role':'user', 'content':f"{prompt}"})
    while sum(len(msg['content']) for msg in context) > 8192:
        context.pop(0)

    response = get_completion_from_messages(context) 

    # Validate JSON
    try:
        json.loads(response)
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response}")
        response = '{}'

    context.append({'role':'assistant', 'content':f"{response}"})
    while sum(len(msg['content']) for msg in context) > 8192:
        context.pop(0)
    return response

def parse_for_movement(json_output):
    """
    This function parses the JSON output from the chatbot and calls the move_c function
    from the map_parser script with the movement key provided by the chatbot.
    """
    start = json_output.find('{')
    end = json_output.rfind('}')

    if start == -1 or end == -1 or start >= end:
        return 'Invalid JSON output.'

    # extract the JSON text
    json_text = json_output[start:end+1]

    # parse the JSON output
    data = json.loads(json_text)

    # retrieve the movement key from the JSON output
    movement_key = data.get("movement", None)

    if movement_key is None:
        return 'No movement key provided in the JSON output.'
    elif movement_key not in ["UP", "DOWN", "LEFT", "RIGHT"]:
        return 'Invalid movement key provided in the JSON output.'
    
    return movement_key

context = [ {'role':'system', 'content':"""
You can ONLY answer questions in the following JSON format outlined in curly brackets:
{
 "inner-thoughts": "<thoughts>",
 "movement": "<movement direction>"
}

the movement key should only be either UP, DOWN, LEFT, RIGHT, or NONE
"""} ]  # accumulate messages

mp.initialize()

color_mapping = {
    '.': '\033[30m.\033[0m',  # black
    'W': '\033[44mW\033[0m',  # blue background
    '#': '\033[47m#\033[0m',  # white background
    'P': '\033[90mP\033[0m',  # gray
    'C': '\033[33mC\033[0m'  # yellow
}

output = f"""
{{ 
    "map": ".PPP#......\\nPPP.#######\\nPPP.......W\\nPP.......WW\\nP........WW\\n.....C..WWW\\n.......WWWW\\n......WWWW#\\n......WWWW#\\n......WWWW#\\n......WWWW#",
    "extra-information": "None"
}}
"""
while True:
    # Parse output into map and extra_information
    output_dict = json.loads(output)
    map = output_dict.get("map").replace('\\n', '\n')
    extra_information = output_dict.get("extra-information")

    prompt = map
    if prompt.lower() == "quit":
        break
    response = get_response(prompt)

    # Parse response into movement_direction and extra_thoughts
    response_dict = json.loads(response)
    movement_direction = response_dict.get("movement")
    extra_thoughts = response_dict.get("inner-thoughts")
    colored_map = ''.join(color_mapping.get(character, character) for character in map)

    os.system('cls')
    print("Map: ")
    print(colored_map)
    print("\n")
    print("Extra Information: ", extra_information)
    print("\n")
    print("----------[ CHARACTER ]----------")
    print("Moving: ", movement_direction)
    print("Thinking About: ", extra_thoughts)
    print("\n")
    print(f"Currently at: {mp.pos_x, mp.pos_y}")
    print(f"Currently standing on: {mp.standing_on()}")
    print(sum(len(msg['content']) for msg in context))
    
    output = mp.move_c(movement_direction)
    time.sleep(0.5)
