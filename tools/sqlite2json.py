import sqlite3

import pandas as pd


def sqlite2json(db_path, table_name, json_path, id="id"):
    with sqlite3.connect(db_path) as conn:
        pd.read_sql_query(f"SELECT * FROM {table_name}", conn, index_col=id).to_json(
            json_path, orient="records", force_ascii=False, indent=4, index=False
        )


def wordfreq():
    sqlite2json(
        r"..\.venv\Lib\site-packages\arramooz\data\wordfreq.sqlite",
        "wordfreq",
        "./data/wordfreq.json",
    )


def nouns():
    sqlite2json(
        r"..\.venv\Lib\site-packages\arramooz\data\arabicdictionary.sqlite",
        "nouns",
        "./data/nouns.json",
    )


def stopwords():
    sqlite2json(
        r"..\.venv\Lib\site-packages\arramooz\data\stopwords.sqlite",
        "stopwords",
        "./data/stopwords.json",
        id="ID",
    )


def q_nouns():
    sqlite2json(
        r"..\.venv\Lib\site-packages\qalsadi\data\custom_dictionary.sqlite",
        "nouns",
        "./data/qalsadi_nouns.json",
    )


if __name__ == "__main__":
    import sys

    match sys.argv[1:]:
        case ["all"]:
            wordfreq()
            nouns()
            stopwords()
            q_nouns()
        case ["ar", "wordfreq"]:
            wordfreq()
        case ["ar", "nouns"]:
            nouns()
        case ["ar", "stopwords"]:
            stopwords()
        case ["qalsadi", "nouns"]:
            q_nouns()
