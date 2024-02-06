import json
from flask import Flask, render_template, request
from trans import Profile, transliterate

app = Flask(__name__)

profile_descriptions = {
    "pausa": ("Pausa", "Ob der Text in Pausa gelesen werden soll"),
    "skip_ta_marbatuh": ("Ta marbuta nicht wiedergeben", "Ob die Ta marbuta am Ende eines Wortes nicht wiedergegeben werden soll"),
}

@app.route('/')
def index():
    # name, value, type, title, description
    profile_data = [
        (
            name, field.default, field.type.__name__, 
            profile_descriptions.get(name, " ".join(name.split("_")).capitalize())
        ) for (name,field) in Profile.__dataclass_fields__.items()
    ]
    return render_template('index.html')

@app.route('/transliterate', methods=['POST'])
def trans():
    """
    Takes a string of Arabic text and settings and returns a transliteration
    """
    data = json.loads(request.data)
    text = data['text']
    profile = Profile(**data['profile'])
    return transliterate(text, profile)



if __name__ == '__main__':
    app.run(debug=True)