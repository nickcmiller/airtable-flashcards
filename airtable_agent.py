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
    def _get_records(base_id: str, table_id: str) -> str:
        try:
            records = get_records(base_id, table_id)
            filtered_records = []
            filtered_records = [
                {
                    "id": record.get("id"), 
                    "Question": record.get("fields", {}).get("Question"),
                    "Answer": record.get("fields", {}).get("Answer")
                }
                for record in records
            ]
            return filtered_records
        except Exception as e:
            return f"Error retrieving records: {str(e)}"

    return {
        "type": "function",
        "function": {
            "name": "get_airtable_records",
            "description": "Retrieves all records from a specified Airtable table",
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
                    }
                },
                "required": ["base_id", "table_id"]
            }
        }
    }, _get_records

if __name__ == "__main__":
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    # print(get_airtable_tables_tool()[1](base_id))

    user_input = f"Find me the Linux table in my base with based_id = {base_id}"
    # user_input = f"Find me a question about sockets in the Linux table in my base with based_id = {base_id}. Give me its record ID"
    
    print(user_input)
    tools = {
        "get_airtable_tables": get_airtable_tables_tool(),
        # "get_airtable_records": get_airtable_records_tool()
    }
    result = react_agent(
        user_input=user_input,
        tools=tools,
        system_instructions="You are an assistant that helps with Airtable-related tasks."
    )
    
    print(result)

    