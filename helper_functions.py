import json
import yaml

def json_to_yaml(
    json_data: str
) -> str:
    """
        Convert a JSON string to YAML.

        Args:
            json_data (str): The JSON data to convert.

        Returns:
            str: The YAML representation of the JSON data.
    """
    import yaml
    data = json.loads(json_data)
    yaml_data = yaml.dump(data, default_flow_style=False)
    return yaml_data