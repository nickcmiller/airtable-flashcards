import os
import json
from typing import List
from pyairtable import Table

from pyairtable import Api, Base
from dotenv import load_dotenv

load_dotenv()

airtable = Api(os.environ.get("AIRTABLE_API_KEY"))

def get_tables(
    base_id: str
) -> List[dict]:
    base = airtable.base(base_id)   
    base_schema = base.schema()
    table_schemas = base_schema.tables

    tables = []
    for table_schema in table_schemas:
        json_table = json.loads(table_schema.json())
        tables.append(json_table)

    return tables


if __name__ == "__main__":
    BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

    tables = get_tables(BASE_ID) 
    for table in tables:
        print(json.dumps(table, indent=4) + "\n")

