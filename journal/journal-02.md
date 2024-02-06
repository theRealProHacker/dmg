# Was bisher geschah

Ich habe erstmal das `Profile` minimiert um den Algorithmus nochmal ganz von vorne aufzusetzen: Zuallererst nutze ich die Bibliothek `qalsadi` (mehr Informationen weiter unten), um den Text zu tokenisieren, lemmatisieren und zu POS-taggen. 

Qalsadi geht nach meinem jetzigen Verständnis folgendermaßen vor:
- Tokenisiere den Text mittels `pyarabic.araby`. Sehr wahrscheinlich muss ich meinen eigenen Tokenisierungsalgorithmus schreiben. 
- Finde für jedes Wort alle möglichen Konfigurationen (Konfiguration: ein großes Dictionary mit allen möglichen grammatikalischen Eigenschaften)
- Fasse die verschiedenen Konfigurationen pro Wort zusammen und finde daraus, unter anderem mittels der Worthäufigkeit, die wahrscheinlichste Schnittmenge. Der genaue Algorithmus dazu ist mir noch nicht klar.
- Daraus kann dann die Wortart und das Lemma bestimmt werden. 

Zuletzt wird wie zuvor eine Reihe von Ersetzungen ausgeführt, die von dem Profil abhängen. 

## Quellen

Taha Zerrouki hat 2020 an der Universität von Tunis eine umfangreiche Doktorarbeit im Bereich NLP im Arabischen abgeschlossen. Er hat im Rahmen dieser Doktorarbeit einige bahnbrechende Pythonbibliotheken entwickelt und veröffentlicht. Ich habe eine Auswahl derer getroffen, die mir in meinem Kontext nützlich erscheinen. 

- [PyArabic](https://github.com/linuxscout/pyarabic) (2010; 2023 erneut wissenschaftlich publiziert): Eine grundlegende Bibliothek zur Manipulierung arabischer Texte auf der alle anderen Bibliotheken aufbauen. 
- [Qalsadi](https://github.com/linuxscout/qalsadi) (2012): Tokenisierung, Lemmatisierung, Affixtrennung, Worthäufigkeiten, POS (kann zwischen Verb, Nomen und Stoppwort unterscheiden) und Wurzelextraktion
- [Qutrub](https://github.com/linuxscout/qutrub): Verbkonjugierung
- [Asma'i](https://github.com/linuxscout/asmai-arabic-semantic): Bestimmung der grammatischen Beziehung arabischer Wörter
- [Mishkal](https://github.com/linuxscout/mishkal/) (2020): Automatische Vokalisierung, [Demo](https://www.tahadz.com/mishkal/)

Die Lizensierung ist durchweg GPL-3.0

Frage ist, inwieweit die Korrektheit dieser Bibliotheken gegeben ist. Zunächst ist dies jedoch irrelevant: Etwas ist besser als Nichts. 

## TODO
- Die Paper zu den genannten Quellen zumindest überfliegen und die Genauigkeit herausfinden/abschätzen
