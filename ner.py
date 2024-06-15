"""Arabic named entity recognition"""

from pyarabic.araby import strip_tashkeel

import data


def find_names(sentences: list[list[str]]):
    for sentence in sentences:
        yield [strip_tashkeel(word) in data.known_names for word in sentence]


# from contextlib import redirect_stderr
# from os import devnull

# import torch
# from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# # Load the model
# torch.device("cuda" if torch.cuda.is_available() else "cpu")
# tokenizer = AutoTokenizer.from_pretrained("hatmimoha/arabic-ner")
# model = AutoModelForTokenClassification.from_pretrained("hatmimoha/arabic-ner")

# nlp = pipeline("ner", model=model, tokenizer=tokenizer)


# def _tag_sentences(sentences: list[str]):
#     with open(devnull, "w") as f, redirect_stderr(f):
#         annotations = nlp(sentences)

#     for sentence in annotations:
#         entities = []
#         tags = []
#         for item in sentence:
#             if item["word"].startswith("##"):
#                 entities[-1] = entities[-1] + item["word"].replace("##", "")
#             else:
#                 entities.append(item["word"])
#                 tags.append(item["entity"])
#         yield entities, tags


# def find_names(sentences: list[list[str]]):
#     """
#     Given a list of lists of unvocalized tokens,
#     returns a generator of lists of whether each token is part of a name.
#     """
#     for sentence, entities in zip(
#         sentences,
#         _tag_sentences(
#             [" ".join(token for token in sentence) for sentence in sentences]
#         ),
#     ):
#         is_name_data = [False] * len(sentence)
#         current_token = 0
#         for entity, tag in zip(*entities):
#             while current_token < len(sentence):
#                 # Possibly use fuzz matching here
#                 if sentence[current_token] == entity:
#                     break
#                 current_token += 1
#             else:
#                 break
#             is_name_data[current_token] = True
#             print(f"{sentence[current_token]}, {tag}")
#         yield is_name_data

# Tests
if __name__ == "__main__":
    from data import known_names


    wiki_input = "data/ner-gold-standard/wiki.txt"


    correct_positive = 0
    correct_negative = 0
    incorrect_positive = 0
    incorrect_negative = 0


    with open(wiki_input, encoding="utf-8") as i:
        for line in i.readlines():
            if not line.strip():
                continue
            word, tag = line.split()
            word = word.removeprefix("‎")
            is_name = tag != "O"
            test_is_name = word in known_names
            if test_is_name:
                if is_name:
                    correct_positive += 1
                else:
                    incorrect_positive += 1
            else:
                if is_name:
                    incorrect_negative += 1
                else:
                    correct_negative += 1

    print(f"{correct_positive=}")
    print(f"{correct_negative=}")
    print(f"{incorrect_positive=}")
    print(f"{incorrect_negative=}")
    print("-"*30)
    print(f"Sum: {correct_positive + correct_negative + incorrect_positive + incorrect_negative}")