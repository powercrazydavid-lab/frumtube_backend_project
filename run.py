#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import asyncio
from dotenv import load_dotenv
import pathlib

env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(os.getenv("SUPABASE_URL"))
print(os.getenv("SUPABASE_KEY"))

from database import db #Your Database class

async def wipe_tables(table_name: str):
    """Delete all data from a table"""
    result = db.supabase.table(table_name).delete().neq("id", "").execute()
    print(f"Deleted {len(result.data or [])} rows from {table_name}")


async def main():

    #List of tables to wipe
    tables = [
        "auth_user",
        "videos"
    ]

    for table in tables:
        await wipe_tables(table)

if __name__ == '__main__':
    main()
