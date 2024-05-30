import json
import re
import sys
from typing import List, Dict

# Get the file path from the command line arguments
file_path = '/Users/nickmiller/Downloads/chat-f3e49400-371a-4ba2-a629-14c782eedf7a.json'


def load_json_from_bolt_file(file_path) -> List[Dict[str, str]]:
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    
    item_dicts = []
    for item in json_data:
        role = item["role"]
        content = item["content"]
        item_dict = {
            "role": role,
            "content": content
        }
        item_dicts.append(item_dict)

    return item_dicts
    



if __name__ == "__main__":
    item_dicts = load_json_from_bolt_file(file_path)
    extracted_text = extract_assistant_text(item_dicts)
    print(json.dumps(extracted_text, indent=4))
    combined_text = "\n".join(extracted_text)
    # print(combined_text)