wiki_input = "data/ner-gold-standard/wiki.txt"
ner_output = "data/ner.json"


def gen_ner_json():
    names = set()
    non_names = set()

    with open(wiki_input, encoding="utf-8") as i:
        for line in i.readlines():
            if not line.strip():
                continue
            word, tag = line.split()
            word = word.removeprefix("‎")
            if tag == "O":
                non_names.add(word)
                names.discard(word)
            elif word not in non_names:
                names.add(word)

    with open(ner_output, "w", encoding="utf-8") as o:
        o.write("[\n")
        o.write(",\n".join(f'"{name}"' for name in names))
        o.write("\n]")
