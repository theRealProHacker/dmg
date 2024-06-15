"""
Farasa (https://farasa.qcri.org/)
"""

import requests
import json

from gen_test import total_unvocalized_file

with open("vocalization/farasa.key", "r", encoding="utf-8") as f:
    key = f.read().strip()

# key = "lpcsTkDIDf"


def seq2seq_diacritization(text):
    url = "https://farasa.qcri.org/webapi/seq2seq_diacritize/"
    dialect = "mor"
    payload = {"text": text, "api_key": key, "dialect": dialect}
    data = requests.post(url, data=payload)
    print(json.loads(data.text))


def diacritization(text):
    url = "https://farasa.qcri.org/webapi/diacritize/"
    payload = {"text": text, "api_key": key}
    data = requests.post(url, data=payload)
    print(data.text)
    print(json.loads(data.text)["text"])


# def diacritization(text):
#     url = 'https://farasa.qcri.org/'

# def diacritization(text):
#     url = 'https://farasa.qcri.org/webapi/diacritize/'
#     text = 'يُشار إلى أن اللغة العربية'
#     api_key = "wmSPrQnPVoogYyAyRm"
#     payload = {'text': text, 'api_key': api_key}
#     data = requests.post(url, data=payload)
#     result = json.loads(data.text)
#     print(result)

# d_func = seq2seq_diacritization
d_func = diacritization

with open(total_unvocalized_file, "r", encoding="utf-8") as f:
    text = ""
    for line in f.readlines():
        if line == "#" * 50 + "\n":
            d_func(text)
            text = ""
            break
            continue
        text += line
    if text:
        ...
