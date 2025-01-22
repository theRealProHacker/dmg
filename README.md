# DMG

DMG is an application that aims to give ease to orientalists, arabists and Islamic scholars in the German-speaking area by providing automatic transliteration. 

The app is currently deployed on PythonAnywhere (https://transliteration.eu.pythonanywhere.com). Try it out now!

# Local deployment

```shell
git clone https://github.com/theRealProHacker/dmg.git
pip install -r requirements.txt
py app.py
```

Now navigate to the localhost URL provided (http://localhost:5000)

If you want to use the LLM IJMES transliteration you have to [make a Huggingface inference API key](https://huggingface.co/docs/api-inference/getting-started#getting-a-token) and insert it in `trans.py/transliterate_llm`

# Features

- Generally letter replacement
- Hyphenation of particles wa-, fa-, sa-, bi-, li-, ka-, al-
- Sun letter assimilation الشَمس: aš-šams
- Detection of idafah and transliteration of ta marbutah as either "t" or "h"/"" accordingly: 
  - &lrm; مَكتَبَةُ كَبيرَة: maktaba kabīra or maktabah kabīrah
  - &lrm; but مَكتَبَةُ الأُستاذِ: maktabat al-ustāḏ
- Consideration of hamzatul wasl
  - &lrm; انْكَسَرَ: inkasara
  - &lrm; الَّذينَ: allaḏīna
  - &lrm; اخرُج: uḫruǧ
  - &lrm; فَانتَقَلَ: fa-ntaqala
  - &lrm; هُم الكُتّاب: hum ul-kuttāb
  - &lrm; عَن الْكِتابُ: ʿan il-kitāb
- Inseration of missing alifs: هَذَا: hāḏā
- Removal of silent letters: قَلوا: qalū
- Nisba as ī: al-ʿarabī
- Many different (boolean) settings
  - whether the text should be transliterated in **pause** or not
  - whether **ta marbutah** should be transliterated as h or not
  - whether **diphthongs** should be transliterated as ai/au or ay/aw
  - whether **geminated half vowels** should be transliterated iyy/uww or īy/ūw
  - whether iyy/uww at the end should always become **ī/ū**
  - whether a **hamza in the first position** should be transliterated
  - whether the personal suffixes **-hu and -hi** should be transliterated as they are pronounced
- Automatic vocalization

# Contributing

Please don't hesitate to raise an issue or to make a pull request. More information for contributing can be found [here](CONTRIBUTING.md)

# License

The software is licensed under CC BY-NC except for the directories `arab_tools` and `data` which are licensed under GPL v3. 
However, the license for `data/ner-gold-standard` is in that directory. 

# Bachelor thesis

This project is part of my bachelor thesis that will be published soon. 
