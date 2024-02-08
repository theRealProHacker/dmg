# Was bisher geschah

Ich habe erstmal das `Profile` minimiert um den Algorithmus nochmal ganz von vorne aufzusetzen: Zuallererst nutze ich die Bibliothek `qalsadi` (mehr Informationen weiter unten), um den Text zu tokenisieren, lemmatisieren und zu POS-taggen. 

Qalsadi geht nach meinem jetzigen Verständnis folgendermaßen vor:
- Tokenisiere den Text mittels `pyarabic.araby`. Sehr wahrscheinlich muss ich langfristig meinen eigenen Tokenisierungsalgorithmus schreiben. 
- Finde für jedes Wort alle möglichen Konfigurationen (Konfiguration: ein großes Dictionary mit allen möglichen grammatikalischen Eigenschaften)
- Fasse die verschiedenen Konfigurationen pro Wort zusammen und finde daraus, unter anderem mittels der Worthäufigkeit, die wahrscheinlichste Schnittmenge. Der genaue Algorithmus dazu ist mir noch nicht klar.
- Daraus kann dann die Wortart und das Lemma bestimmt werden. 

Zuletzt wird wie zuvor eine Reihe von Ersetzungen ausgeführt, die von dem Profil abhängen. 

## Probleme

Die Reihenfolge der Schritte ist mir noch nicht ganz klar:

Soll die Präfixbestimmung vor oder nach dem Ersetzen der Buchstaben kommen? Bzw. soll die Präfixbestimmung im Arabischen, im Deutschen oder gleichzeitig stattfinden. Das Problem ist, dass ich mich (zumindest teilweise) festlegen muss, aber noch gar nicht weiß, was am Ende mehr Sinn machen wird. Das Gleiche gilt für die Namensbestimmung.

Ich bin bis jetzt zu dem Schluss gekommen, dass es mehr Sinn macht diese beiden Dinge im Arabischen zu klären. Ich vergesse aber jedes Mal, wie ich zu diesem Schluss gekommen bin. Ich weiß nur, dass ich einen guten Grund hatte. 

Die andere, rein technische, Problematik ist, dass `qalsadi` eine SQLite Datenbank zum Cachen nimmt (warum nicht einfach eine LRU Cache im RAM speichern, das sollte für die meisten Anwendungsfälle reichen?). Diese Datenbank wird jedoch aufgrund des Flask-Multithreading in einem anderen Thread verwendet, als sie erstellt wird, was wiederum das Programm zum Absturz bringt 🤦. Es gibt einige Lösungswege:

1. Ich forke `qalsadi` und ändere alles, was mich stört
2. Ich leite den SQL-Cursor auf ein Mock-Cursor um, der immer ein Cache-Miss produziert
3. (ähnlich wie) Ich Ctrl+C/Ctrl+V den gesamten Code, den ich brauche und entferne alle Aufrufe zur SQLite Datenbank
4. Ich sorge dafür, dass die Datenbank im gleichen Thread erstellt wird, wie der Serverthread -> Wird schwer
5. Ich benutze `qalsadi` und alle entlehnten Bibliotheken nicht -> wäre wahrscheinlich ein großer Verlust

## Quellen

Taha Zerrouki hat 2020 an der Universität von Tunis eine umfangreiche Doktorarbeit im Bereich NLP im Arabischen abgeschlossen. Er hat im Rahmen dieser Doktorarbeit einige bahnbrechende Pythonbibliotheken entwickelt und veröffentlicht. Ich habe eine Auswahl derer getroffen, die mir in meinem Kontext nützlich erscheinen. 

- [PyArabic](https://github.com/linuxscout/pyarabic) (2010; 2023 erneut wissenschaftlich publiziert): Eine grundlegende Bibliothek zur Manipulierung arabischer Texte auf der alle anderen Bibliotheken aufbauen. 
- [Qalsadi](https://github.com/linuxscout/qalsadi) (2012): Tokenisierung, Lemmatisierung, Affixtrennung, Worthäufigkeiten, POS (kann zwischen Verb, Nomen und Stoppwort unterscheiden) und Wurzelextraktion
- [Qutrub](https://github.com/linuxscout/qutrub): Verbkonjugierung
- [Asma'i](https://github.com/linuxscout/asmai-arabic-semantic): Bestimmung der grammatischen Beziehung arabischer Wörter
- [Mishkal](https://github.com/linuxscout/mishkal/) (2020): Automatische Vokalisierung, [Demo](https://www.tahadz.com/mishkal/)

Die Lizensierung ist durchweg GPL-3.0

Frage ist, inwieweit die Korrektheit und Genauigkeit dieser Bibliotheken gegeben ist. Zunächst ist dies jedoch irrelevant: Etwas ist besser als Nichts. 

## TODO
- Rausfinden (ausprobieren), ob es besser ist Präfix- und Eigennamenbestimmung nach oder vor der Buchstabenersetzung zu tun und Grund aufschreiben
- Das `qalsadi` SQLite Problem lösen
- Im Web (aka Internetz) hosten -> MVP und testen
- Einen Transliterationsexperten bekommen -> Meine alte Arabischlehrerin hat sich noch nicht zurückgemeldet
- Die Paper zu den genannten Quellen zumindest überfliegen und die Genauigkeit herausfinden/abschätzen

