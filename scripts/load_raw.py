"""
Imports member data from CSV to local DuckDB file without transformation or casting.
"""

import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DB = ROOT / "member_analytics.duckdb"

TABLES = {
    "raw_membership": ["members", "contracts"],
    "raw_access": ["checkins"],
    "raw_masterdata": ["studios"],
}


def main() -> None:
    con = duckdb.connect(str(DB))
    for schema, tables in TABLES.items():
        con.execute(f"create schema if not exists {schema}")
        for t in tables:
            csv = RAW / f"{t}.csv"
            if not csv.exists():
                raise FileNotFoundError(f"{csv} missing, run scripts/generate_data.py first")
            con.execute(f"create or replace table {schema}.{t} as select * from read_csv_auto('{csv}', header=true)")
            n = con.execute(f"select count(*) from {schema}.{t}").fetchone()[0]
            print(f"{schema}.{t:<12} {n:>9,}")
    con.close()
    print(f"-> {DB}")


if __name__ == "__main__":
    main()