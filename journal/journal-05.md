# UI

Ich habe folgendes hinzugefügt:

- Dark/Light-Mode
- Ein cooles Farbscheme
- Ein Feedback-Formular
- Zwei coole Fonts: Google Sans und Scheherazade New
- Falls in das Inputfeld kopiert wird, wird es sofort transliteriert
- Durch Klicken auf das Outputfeld, wird der Inhalt automatisch kopiert. 

# Zahlen, Satzzeichen und Representation

Ich habe Daten für Satzzeichen, Zahlen und Repräsentationen hinzugefügt. 

- Arabisch nutzt arabisch-indische Zahlen. Diese werden in die "deutschen" arabischen Zahlen umgewandelt. Weitere "Zahlzeichen" sind Dezimaltrennzeichen, Tausendertrennzeichen, Prozentzeichen, usw.
- Die Satzzeichen ".,!?" sind implementiert
- Jeder Buchstabe hat seine Repräsentationszeichen, die den Buchstaben an einer bestimmten Stelle zeigen. Diese werden jeweils in ihre allgemeine Form umgewandelt

# NER

Folgende Quellen gibt es:

- [Huggingface](https://huggingface.co/search/full-text?q=named entity recognition arabic) (KI-Modelle):
    - [Arabic NER](https://huggingface.co/hatmimoha/arabic-ner) ungefähr ein Jahr alt
    - [Wojood](https://huggingface.co/SinaLab/ArabicWojood-FlatNER) von Mai 2022
    - [Multilingual BERT NER](https://huggingface.co/Davlan/bert-base-multilingual-cased-ner-hrl) mehr als ein Jahr alt
    - [Dialectal Arabic XLM-R Base](https://huggingface.co/3ebdola/Dialectal-Arabic-XLM-R-Base) für dialektisches Arabisch von 2022
- [AraGPT2](https://link.springer.com/chapter/10.1007/978-3-031-41774-0_18) von September 2023
    - Auch [auf Huggingface](https://huggingface.co/aubmindlab/aragpt2-base)
- [SVM-based (Support Vector Machine) approach](https://www.semanticscholar.org/paper/Arabic-Named-Entity-Recognition%3A-An-SVM-based-Benajiba-Diab/67b4b59aa65c5f65c47deff75c3bf5386b129e92)
- [NERA](https://www.researchgate.net/publication/264209725_NERA_Named_entity_recognition_for_Arabic) von 2009

Ein Problem ist, dass die Tokens möglicherweise verschieden sind. Entweder muss man dann die Tokens einfach so nehmen wie sie sind, oder man muss irgendwie die Tokens matchen ohne dabei einen Fehlerzustand ausgeben zu dürfen. 

Ich habe einfach gleich das erste Modell ausprobiert und es scheint gut genug zu funktionieren. Leider erhöht es mit seinen 110 Millionen Parametern jedoch erheblich die Laufzeitkosten sowohl beim Start als auch bei jeder Transliteration. Die Tests, die vorher in weniger als einer Sekunde gelaufen sind, sind jetzt erst nach fast einer halben Minute fertig. Und die langsame NER führt aufgrund von fehlendem Caching auch im Frontend zu Lags. 

Noch beunruhigender ist jedoch, dass mein Hosting ein maximales File-Limit von 512 MB anbietet, was absolut nicht ausreicht, um pytorch, geschweige denn das trainierte Modell herunterzuladen. Wegen diesen Problemen, habe ich das Feature vorerst entfernt. Ich werde jedoch weitere Wege ausprobieren, die vielleicht weniger rechenintensiv sind. 

# Diphthonge

Es gibt nun eine Option, Diphthonge als solche wiederzugeben: also "au" statt "aw" und "ai" statt "ay".

# Doppelte Vokale

Es gibt nun eine Option "Doppelte Vokale", die by default angeschaltet ist und dann die Halbvokale doppelt wiedergibt: also "quwwah" anstatt "qūwa"