import os
import json
from typing import List, Optional

from pyairtable import Table
from pyairtable import Api, Base
from dotenv import load_dotenv

load_dotenv()

airtable = Api(os.environ.get("AIRTABLE_API_KEY"))

def get_tables(
    base_id: str
) -> List[dict]:
    """
        Gets all tables in a base.

        Args:
            base_id (str): The id of the base to get tables from.

        Returns:
            List[dict]: A JSON list of tables
    """
    base = airtable.base(base_id)   
    base_schema = base.schema()
    table_schemas = base_schema.tables

    tables = []
    for table_schema in table_schemas:
        json_table = json.loads(table_schema.json())
        tables.append(json_table)

    return tables

def get_fields(
    base_id: str,
    table_id: str
) -> List[dict]:
    """
        Get all fields from a given table in a given base.

        Args:
            base_id (str): The id of the base.
            table_id (str): The id of the table.

        Returns:
            List[dict]: A JSON list of fields.
    """
    tables = get_tables(base_id)
    filtered_tables = [table for table in tables if table['id'] == table_id]
    fields = filtered_tables[0]['fields']

    return fields

def get_records(
    base_id: str,
    table_id: str
) -> List[dict]:
    """
        Get all records from a given table in a given base.

        Args:
            base_id (str): The id of the base.
            table_id (str): The id of the table.

        Returns:
            List[dict]: A JSON list of records.
    """
    tables = get_tables(base_id)
    table = airtable.table(base_id, table_id)
    records = table.all()

    return records

if __name__ == "__main__":
    BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
    TABLE_TEST_ID = os.environ.get("AIRTABLE_TABLE_TEST_ID")

    tables = get_tables(BASE_ID) 

    fields = get_fields(BASE_ID, TABLE_TEST_ID)

    records = get_records(BASE_ID, TABLE_TEST_ID)
    print(len(records))

    

