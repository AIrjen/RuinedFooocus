import ollama # needs ollama to run locally
import re
import json

#Should be a setting? llama 3 is good enough and fits in a decent amount of VRAM.
LLMmodelname = 'llama3'

# Pull the model, if necessary
# will automatically download on first start if the model isnt there.
ollama.pull(LLMmodelname)



def mad_libs(prompt):
    processed_prompt = ""
    while processed_prompt == "":
        # Would be great to put the LLM prompts in a setting file
        assistant_response = one_shot_llm_response(LLMmodelname, "Can you do some sentence work for me? Don't leave any blanks, you decide the words to put in. Don't change any other words in the sentence. Replace the _____ with some words from the following sentence: " + prompt + ".  The output must be a JSON object with <prompt>." )
        processed_prompt = get_prompt_from_json(extract_json(assistant_response))
    return processed_prompt


def one_shot_llm_response(LLMmodelname, input_text):
    try:
        
        # Create a single message with the user's input
        message = {
            'role': 'user',
            'content': input_text,
        }

        # Pass the message to the chat function
        response = ollama.chat(model=LLMmodelname, messages=[message], keep_alive=0,) # keep_alive 0 turns the model off after the question, freeing up the memory for image gens (for us 8Gb peeps)

        # Assuming the response structure has 'message' and 'content'
        if 'message' in response and 'content' in response['message']:
            assistant_response = response['message']['content']
            #print(assistant_response)
            #print(extract_json(assistant_response))
            #print(get_prompt_from_json(extract_json(assistant_response)))
            return assistant_response
        else:
            ("Unexpected response structure:", response)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_json(s):
    """
    Extracts the first JSON object found in a given string.

    Args:
        s (str): The input string containing potential JSON data.

    Returns:
        str: The extracted JSON object, or None if no valid JSON was found.
    """

    # Regular expression pattern to match JSON objects
    json_pattern = r'{[^}]*}'
    
    # Find the first occurrence of a JSON object in the string
    match = re.search(json_pattern, s)
    
    # If a JSON object is found, return it; otherwise, return None
    if match:
        return match.group()
    else:
        return None
    

def get_prompt_from_json(s):
    """
    Extracts and returns the prompt value from a given JSON string.

    Args:
        s (str): The input JSON data as a string.

    Returns:
        str: The extracted prompt, or an empty string if no valid JSON was found.
    """

    # If there's no JSON to parse, return an empty string
    if not s:
        return ""

    try:
        s = s.replace('<prompt>', 'prompt')
        s = s.replace('''prompt''', 'prompt')
        s = s.replace('""prompt""', 'prompt')
        json_data = json.loads(s)
        
        
        # Check for keys "prompt", 'prompt', or <prompt>
        prompt_keys = ["prompt"]
        
        # Find a match for any of these keys in the JSON data
        for key in prompt_keys:
            if key in str(json_data):
                return json_data[key]
    
    except (json.JSONDecodeError):
        # If there's a JSON decoding error, return an empty string
        pass
    
    # Return an empty string as the default value
    return ""

    