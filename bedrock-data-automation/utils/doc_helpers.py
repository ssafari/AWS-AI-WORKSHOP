import json

def read_json_file_to_string(filename):
    ''' read JSON file and parse contents '''
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"Data type: {type(data)}")
        #convert python object to json string format
        json_text = json.dumps(data)
        print(f"Json string format: {json_text}")
        return json_text
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file. Check for malformed JSON data.")
    return None
