import json

from flask import Flask, render_template, request

from trans import Profile, transliterate

app = Flask(__name__)


@app.route("/")
def index():
    # name, value, type, title, description
    profile = [
        (
            name,
            field.default,
            field.type.__name__,
            *Profile.descriptions.get(
                name, (" ".join(name.split("_")).capitalize(), "")
            ),
        )
        for (name, field) in Profile.__dataclass_fields__.items()
    ]
    return render_template("index.html", profile=profile)


@app.route("/transliterate", methods=["POST"])
def trans():
    """
    Takes a string of Arabic text and settings and returns a transliteration
    """
    data = json.loads(request.data)
    text = data["text"]
    profile = Profile(**data["profile"])
    return transliterate(text, profile)

@app.route("/feedback", methods=["POST"])
def feedback():
    with open("feedback.jsonl", "ab") as f:
        f.write(request.data + b"\n")
    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
