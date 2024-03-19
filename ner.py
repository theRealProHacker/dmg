""" Arabic named entity recognition """
from contextlib import redirect_stderr
from os import devnull

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# Load the model
torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("hatmimoha/arabic-ner")
model = AutoModelForTokenClassification.from_pretrained("hatmimoha/arabic-ner")

nlp = pipeline("ner", model=model, tokenizer=tokenizer)


def _tag_sentences(sentences: list[str]):
    with open(devnull, "w") as f, redirect_stderr(f):
        annotations = nlp(sentences)

    for sentence in annotations:
        entities = []
        tags = []
        for item in sentence:
            if item["word"].startswith("##"):
                entities[-1] = entities[-1] + item["word"].replace("##", "")
            else:
                entities.append(item["word"])
                tags.append(item["entity"])
        yield entities, tags


def find_names(sentences: list[list[str]]):
    """
    Given a list of lists of unvocalized tokens,
    returns a generator of lists of whether each token is part of a name.
    """
    for sentence, entities in zip(
        sentences,
        _tag_sentences(
            [" ".join(token for token in sentence) for sentence in sentences]
        ),
    ):
        is_name_data = [False] * len(sentence)
        current_token = 0
        for entity, tag in zip(*entities):
            while current_token < len(sentence):
                # Possibly use fuzz matching here
                if sentence[current_token] == entity:
                    break
                current_token += 1
            else:
                break
            is_name_data[current_token] = True
            debug(f"{sentence[current_token]}, {tag}")
        yield is_name_data
