"""
Module for vocalization of Arabic text
"""

# Using mishkal
# See: https://github.com/linuxscout/mishkal?tab=readme-ov-file#example

# import json

from contextlib import suppress
import mishkal.tashkeel

# import requests
import data

vocalizer = mishkal.tashkeel.TashkeelClass("")


def vocalize(text: str) -> str:
    o = vocalizer.tashkeel(text)
    o = "".join(c if c.isprintable() else " " for c in o).strip()
    return o


# This doesn't work
# def vocalize(text: str) -> str:
#     task = "diacritization"
#     data = {"text": text, "task": task, "API_KEY": "lpcsTkDIDf"}
#     response = requests.post(
#         "https://farasa.qcri.org/diacritization/analyze/",
#         data=data,
#     )
#     response.raise_for_status()
#     return json.loads(response.text)["text"]


def vocalize(text: str) -> str:
    from gradio_client import Client

    client = Client("https://testingdoang-shakkala-arabic-tashkeel.hf.space/")
    return client.predict(text, api_name="/predict")


# fix asmai from here

with suppress(ImportError):
    import asmai.semdictionary  # noqa

    asmai.semdictionary.SemanticDictionary.lookup_rule = (
        lambda self, primate_word, second_word: data.sem_relations.get(
            (primate_word, second_word), False
        )
    )
