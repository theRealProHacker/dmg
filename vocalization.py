"""
Module for vocalization of Arabic text
"""

# Using mishkal
# See: https://github.com/linuxscout/mishkal?tab=readme-ov-file#example

import mishkal.tashkeel

vocalizer = mishkal.tashkeel.TashkeelClass("")


def vocalize(text: str) -> str:
    o = vocalizer.tashkeel(text)
    o = "".join(c if c.isprintable() else " " for c in o).strip()
    return o


# fix asmai from here

import asmai.semdictionary  # noqa

asmai.semdictionary.SemanticDictionary.lookup_rule = (
    lambda self, primate_word, second_word: False
)
