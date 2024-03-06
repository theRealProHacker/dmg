import sqlite3

import pandas as pd


def sqlite2json(db_path, table_name, json_path):
    with sqlite3.connect(db_path) as conn:
        pd.read_sql_table(table_name, conn, index_col="id").to_json(
            json_path, orient="records", force_ascii=False, indent=4, index=False
        )


if __name__ == "__main__":
    sqlite2json(
        r".venv\Lib\site-packages\arramooz\data\wordfreq.sqlite",
        "wordfreq",
        "../data/wordfreq.json",
    )
