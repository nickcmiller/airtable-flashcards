import os
import json

from airtable_functions import get_tables, get_records
from agent_functions import react_agent

BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

def get_airtable_tables_tool():
    def _get_tables(
        base_id: str
    ) -> str:
        try:
            tables = get_tables(base_id)
            filtered_tables = []
            filtered_tables = [
                {
                    "id": table.get("id"), 
                    "name": table.get("name"),
                    "fields": table.get("fields"),
                    "primary_field_id": table.get("primary_field_id")
                }
                for table in tables
            ]
            return json.dumps(filtered_tables)
        except Exception as e:
            return f"Error retrieving tables: {str(e)}"

    return {
        "type": "function",
        "function": {
            "name": "get_airtable_tables",
            "description": "Retrieves all tables from a specified Airtable base",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_id": {
                        "type": "string",
                        "description": "The ID of the Airtable base to retrieve tables from"
                    }
                },
                "required": ["base_id"]
            }
        }
    }, _get_tables

def get_airtable_records_tool():
    def _get_records(
        base_id: str,
        table_id: str, 
        fields: list = None
    ) -> str:
        try:
            records = get_records(base_id, table_id)
            filtered_records = []
            for record in records:
                record_data = {"id": record.get("id")}
                if fields:
                    for field in fields:
                        record_data[field] = record.get("fields", {}).get(field)
                else:
                    record_data.update(record.get("fields", {}))
                filtered_records.append(record_data)
            return filtered_records
        except Exception as e:
            return f"Error retrieving records: {str(e)}"

    return {
        "type": "function",
        "function": {
            "name": "get_airtable_records",
            "description": "Retrieves records from a specified Airtable table, optionally filtering fields",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_id": {
                        "type": "string",
                        "description": "The ID of the Airtable base"
                    },
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the Airtable table"
                    },
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Optional list of field names to include in the output. If not provided, all fields will be returned."
                    }
                },
                "required": ["base_id", "table_id"]
            }
        }
    }, _get_records



if __name__ == "__main__":
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    # print(get_airtable_tables_tool()[1](base_id))

    user_input = f"""
    Find the Linux table. From that table, return records related to security, if any, to me as JSON list. Include Last Modified in the response.
    Don't preface the response with anything, just return the JSON list.
    ```
    [
        {{
            "Question": "", 
            "Answer": "", 
        }},
        {{
            "Question": "", 
            "Answer": "", 
        }}
    ]
    ```
    base_id: {base_id}
    """
    # user_input = f"Find me a question and answer for all the records in the Linux table and when they were last modified. based_id: {base_id}"
    
    print(user_input)
    tools = {
        "get_airtable_tables": get_airtable_tables_tool(),
        "get_airtable_records": get_airtable_records_tool()
    }
    result = react_agent(
        user_input=user_input,
        tools=tools,
        system_instructions="You are an assistant that helps with Airtable-related tasks. You may be asked to reflect on and modify the data you have retrieved from Airtable."
    )
    
    print(result)

    