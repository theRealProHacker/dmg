import json

from flask import Flask, render_template, request

import book
import data
from data_types import IJMESProfile, NameProfile, Profile, profile_descriptions
from trans import transliterate, transliterate_ijmes
from vocalization import vocalize

app = Flask(__name__)


# Pages
@app.route("/")
def index():
    # name, value, type, title, description
    profile = [
        (
            name,
            field.default,
            field.type.__name__,
            *profile_descriptions.get(
                name, (" ".join(name.split("_")).capitalize(), "", "", "")
            ),
        )
        for (name, field) in Profile.__dataclass_fields__.items()
    ]
    return render_template(
        "index.html", profile=profile, input_map=data.input_conversion_map
    )


@app.route("/names")
def names():
    profile = [
        (
            name,
            field.default,
            field.type.__name__,
            *profile_descriptions.get(
                name, (" ".join(name.split("_")).capitalize(), "", "", "")
            ),
        )
        for (name, field) in NameProfile.__dataclass_fields__.items()
    ]
    return render_template(
        "names.html", profile=profile, input_map=data.input_conversion_map
    )


@app.route("/ijmes")
def ijmes():
    return render_template("ijmes.html", input_map=data.input_conversion_map)


@app.route("/book")
def _book():
    return render_template(
        "book.html", toc=book.toc_html, content=book.content, input_map=book.input_map
    )


# API endpoints


@app.route("/transliterate", methods=["POST"])
def trans():
    """
    Takes a string of Arabic text and settings and returns a transliteration
    """
    data = json.loads(request.data)
    text = data["text"]
    profile = Profile(**data["profile"])
    return transliterate(text, profile)


@app.route("/transliterate/names", methods=["POST"])
def trans_names():
    data = json.loads(request.data)
    text = data["text"]
    profile = NameProfile(**data["profile"])
    return transliterate(text, profile)


@app.route("/transliterate/ijmes", methods=["POST"])
def trans_ijmes():
    data = json.loads(request.data)
    text = data["text"]
    profile = IJMESProfile(**data["profile"])
    return transliterate_ijmes(text, profile)


@app.route("/vocalize", methods=["POST"])
def vocalization():
    """
    Takes a string of Arabic text and returns a vocalized version
    """
    text = request.data.decode("utf-8")
    return vocalize(text)


@app.route("/feedback", methods=["POST"])
def feedback():
    with open("feedback.jsonl", "ab") as f:
        f.write(request.data + b"\n")
    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
