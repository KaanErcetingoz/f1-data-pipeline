"""Load bronze JSON files into the raw schema of the DuckDB database."""

from pathlib import Path

import duckdb

DATABASE_PATH = Path("data/f1.duckdb")
BRONZE_PATH = Path("data/bronze")
FOLDERS = ["driver_standings", "constructor_standings", "race_winners"]


def load_folder(con: duckdb.DuckDBPyConnection, folder: str) -> None:
    """Replace the raw table for one bronze folder with one row per JSON file."""
    con.sql(
        f"""
        CREATE OR REPLACE TABLE raw.{folder} AS
        SELECT
            filename,
            content::JSON AS payload
        FROM read_text('{BRONZE_PATH}/{folder}/*.json')
        """
    )


def main() -> None:
    """Create the raw schema and load every bronze folder into it."""
    with duckdb.connect(DATABASE_PATH) as con:
        con.sql("CREATE SCHEMA IF NOT EXISTS raw")
        for folder in FOLDERS:
            load_folder(con, folder)
            print(f"loaded raw.{folder}")
        con.sql("SHOW ALL TABLES").show()


if __name__ == "__main__":
    main()
