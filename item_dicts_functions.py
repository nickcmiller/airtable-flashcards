def extract_assistant_text(item_dicts: List[Dict[str, str]]) -> str:
    
    assistant_text_list = []

    for item in item_dicts:
        if item["role"] == "assistant":
            assistant_text_list.append(item["content"])

    assistant_text = "\n".join(assistant_text_list)

    return assistant_text