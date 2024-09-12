import os

from airtable_functions import get_tables

BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

tables = get_tables(BASE_ID)
print(tables)
