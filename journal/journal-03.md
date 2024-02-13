# Neuigkeiten und Fortschritte

## UI

Es gibt nun eine Fehlermeldung, wenn die Serveranfrage fehlschlägt

### Webhosting

Eine erste Version ist online verfügbar auf https://transliteration.eu.pythonanywhere.com/

Die Server stehen in Deutschland und der Service ist kostenlos. Ich werde hier der Vollständigkeit halber kurz erläutern, wie das Aufsetzen funktioniert:

1. Kostenloses Konto auf [eu.pythonanywhere.com](https://eu.pythonanywhere.com) mit dem richtigen Benutzernamen machen (in diesem Fall transliteration)
2. Webapp erstellen und Flask mit app bei `app.py` aus den Optionen auswählen
3. `git clone [repo-github-url]`
4. `cd [repo]`, `python3 -m venv venv`, `. venv/bin/activate`, `pip install -r requirements.txt`
5. Den Pfad zum Sourcecode und zum `venv` bei der Webapp configuration angeben: 
    - `/home/transliteration/[repo]`
    - `/home/transliteration/[repo]/venv`
7. Die Webapp neustarten

### TODOs (perspektivisch)

- besseres Design
- Profile-Erweiterung für andere Arten von Attributen (nicht nur booleans)

## Anderes

Anscheinend hatte keiner von den Islamwissenschaftlern aktiv Interesse daran, mir zu helfen. Ich habe es jetzt noch einmal bei den Arabisten probiert.

Trotz der Probleme mit qalsadi, konnte ich ein großes Stück weiterkommen. Ich konnte mittels Methode 3 des letzten Journals (Ich Ctrl+C/Ctrl+V den gesamten Code, den ich brauche und entferne alle Aufrufe zur SQLite-Datenbank) die SQLite-Problematik vorerst lösen. SQLite-Datenbanken werden zum Speichern der Wortfrequenzdaten und als Wörterbuch verwendet. Ich habe bis auf Weiteres die Frequenz aller Wörter auf 0 gesetzt. 

Auch sonst konnte ich etwas tieferen Einblick in den Code gewinnen und kann jetzt etwas Pseudocode mit Ergebnissen demonstrieren:

```py
# Zum tokenizen wird auf dem regex-Pattern "([\w\u0670\u064b-\u0652']+)" gematcht (Buchstaben + diakritische Zeichen)
tokens = tokenize(text)

# Die vier Tags sind: t: Stopwort, n: Nomen, v: Verb, nv: ?
# Wie genau die Tags vergeben werden, kann ich leider noch nicht verstehen
# Ich weiß aber wo der Code und die Daten dafür liegen (in tashaphyne und naftawayh)
tags = [tag_word(token) for token in tokens]

# Hier werden alle Möglichkeiten generiert
analyzed = [check_word(token, tag) for token, tag in zip(tokens, tags)]

# Aus diesen Möglichkeiten wird eine wahrscheinlichste gemacht
stemnodelist = analyze(analyzed) # Mir ist bewusst, dass die Benennung sub-optimal ist

# Aus dieser Wahrscheinlichsten wird Lemma und Tag gezogen
lemmas = get_lemmas(stemnodelist, return_pos=True)
```

```py
def check_word(word, tag):
    # Die gesamte Idee von diesem Code ist alle möglichen "Wortarten" 
    # (Satzzeichen, Zahlen, Stopwörter, Verben und Nomen) 
    # durchzugehen und dabei alle Möglichkeiten als StemmedWord zurückzugeben
    # Wie so ein StemmedWord aussieht sehen wir später
    # Auf jeden Fall nutzen wir dazu vier Stemmer (stopword, verb, noun und unknown)
    # Auch hier gilt, dass ich keine Ahnung habe, wie genau das Stemmen jeweils abläuft
    word_nm = araby.strip_tashkeel(word)
    word_nm_shadda = araby.strip_harakat(word)

    if stemmed := self.check_word_as_numeric(word_nm):
        return [stemmed]

    if stemmed := self.check_word_as_punct(word_nm):
        return [stemmed]

    result = []

    if araby.is_arabicword(word_nm):
        if word in qalsadi.stopwords.STOPWORDS:
            result += stopwordstemmer.stemming_stopword(word_nm)
        if not any(c in ("ة", *araby.TANWIN) for c in word) and (
            tagger.has_verb_tag(tag) or tagger.is_stopword_tag(tag)
        ):
            result += verbstemmer.stemming_verb(word_nm)
        if tagger.has_noun_tag(tag) or tagger.is_stopword_tag(tag):
            result += nounstemmer.stemming_noun(word_nm)

    if not result:
        result = unknownstemmer.stemming_noun(word_nm)

    
    result = [
        x
        for x in result
        if araby.shaddalike(word_nm_shadda, x.vocalized)
        and x.unvocalized == word_nm
    ]

    result = self.check_partially_vocalized(word, result)

    add_frequencies(result)

    if not result:
        ... # error handling
    return [StemmedWord(w) for w in result]
```

```py
# Ist (noch) nicht mein Code
def analyze(self, detailed_stemming_dict):
    stemnode_list = []
    for stemming_list in detailed_stemming_dict:
        stemnode_list.append(stemnode.StemNode(stemming_list, True))
    return stemnode_list

def get_lemmas(self, stemnode_list, pos="", return_pos = False):
    lemmas = []
    for stnd in stemnode_list:
        lemmas.append(stnd.get_lemma(pos=pos, return_pos=return_pos))
    return lemmas
```

```py
# Ausgaben für einfaches Beispiel

# wort
"يَكْتُبُ الكَلْبُ" # Der Hund schreibt

# tags
'يَكْتُبُ', 'الكَلْبُ'

# analyzed
[[{
    u'word' = u'يكتب', # yaktub (er schreibt)
    u'vocalized' = u'يَكْتُبُ', 
    u'unvocalized' = u'',
    u'semivocalized' = u'يَكْتُب',
    # Ich verstehe hiervon nur so viel: 3.P Sg M Präsens/Imperfekt Indikativ
    # Die tags werden, aber unten noch einmal einzeln aufgezählt
    u'tags' = u'المضارع المعلوم:هو:y:مدخل مشكول:',
    # scheint das zu sein 
    # 'affix': (word_seg['pro'], word_seg['prefix'], word_seg['suffix'], word_seg['enc']),
    u'affix_key' = u'-ي--|المضارع المعلوم:هو:y:مدخل مشكول',
    # Aus dem Stamm können viele andere Arten von Wörtern gebildert werden, z.B. kaatib (das Buch)
    u'stem' = u'كتب',
    u'original_tags' = u'('',)',
    u'freq' = u'0', # von mir so gesetzt
    u'type' = u'Verb',
    u'original' = u'كَتَبَ',
    u'tag_regular' = u'True',
    u'root' = u'كتب',
    u'affix' = u'Taha', # ?
    u'action' = u'',
    u'object_type' = u'',
    u'need' = u'',
    u'tag_type' = u'2',
    u'tag_added' = u'False',
    u'tag_initial' = u'False',
    u'tag_transparent' = u'False',
    u'tag_mamnou3' = u'False',
    u'tag_break' = u'False',
    u'tag_voice' = u'معلوم',
    u'tag_mood' = u'مرفوع',
    u'tag_confirmed' = u'',
    u'tag_pronoun' = u'هو',
    u'tag_transitive' = u'True',
    u'tag_person' = u'4',
    u'tag_original_number' = u'مفرد',
    u'tag_original_gender' = u'مذكر',
    u'tag_number' = u'1',
    u'tag_gender' = u'1',
    u'tag_tense' = u'المضارع المعلوم',
}], [{
    u'word' = u'الكلب', # al-kalb (der Hund)
    u'vocalized' = u'الْكَلْبُ',
    u'unvocalized' = u'',
    u'semivocalized' = u'الْكَلْب',
    u'tags' = u'تعريف:مرفوع:متحرك:ينون::مدخل مشكول:',
    # Hier sehen wir, dass die Affixbestimmung hier schon geschieht. 
    # Die Frage ist, wie können wir das sicher gezielt herausgreifen (was ist das Muster)?
        # Antwort: .split("-")[0]
    u'affix_key' = u'ال--ُ-|الكلب',
    u'stem' = u'كلب',
    u'original_tags' = u'('',)',
    u'freq' = u'0',
    u'type' = u'Noun::جامد',
    u'original' = u'كَلْبٌ',
    u'tag_regular' = u'True',
    u'root' = u'كلب',
    u'affix' = u'Taha',
    u'action' = u'',
    u'object_type' = u'',
    u'need' = u'',
    u'tag_type' = u'4',
    u'tag_added' = u'False',
    u'tag_initial' = u'False',
    u'tag_transparent' = u'False',
    u'tag_mamnou3' = u'False',
    u'tag_break' = u'False',
    u'tag_voice' = u'False',
    u'tag_mood' = u'False',
    u'tag_confirmed' = u'False',
    u'tag_pronoun' = u'False',
    u'tag_transitive' = u'False',
    u'tag_person' = u'4',
    u'tag_original_number' = u'مفرد',
    u'tag_original_gender' = u'مذكر',
    u'tag_number' = u'1',
    u'tag_gender' = u'1',
}]]

# stemnodelist
# Man kann hier sehen, dass im Endeffekt aufsummiert wurde,
# auch wenn der Print ein bisschen broken scheint
[
'يكتب':كَتَبَ, [verb-non_break]{V:1, N:0, S:0} {'mansoub': [], 'marfou3': [0], 'majrour': [], 'majzoum': [], 'tanwin_mansou  ub': [], 'tanwin_marfou3': [], 'tanwin_majrour': []}{'verb': [0], 'noun': [], 'pounct': [], 'stopword': []}{'كَتَبَ': [0]}In  ndexes : [0],
'الكلب':كَلْبٌ, [noun-non_break]{V:0, N:1, S:0} {'mansoub': [], 'marfou3': [0], 'majrour': [], 'majzoum': [], 'tanwin_mansoub': [], 'tanwin_marfou3': [], 'tanwin_majrour': []}{'verb': [], 'noun': [0], 'pounct': [], 'stopword': []}{'كَلْبٌ': [0]}I  Indexes : [0]]

# lemma mit POS
[('كَتَبَ', 'verb'), ('كَلْبٌ', 'noun')]
```

## Neue To-Dos

Herausfinden, was genau die Wortarten eigentlich bedeuten. Was ist zum Beispiel mit Pronomen und Partizipien (der Rest scheint relativ klar)? Ist es möglich eine noch feinere Unterscheidung zu tätigen?

Die Tokenisierung und Satzerkennung gefällt mir noch nicht so. Insbesondere, was mit Satzzeichen, Leerzeichen, Zahlen und nicht-arabischen Buchstaben passiert ist noch nicht klar festgelegt (also vom Code natürlich schon). Sollte ein Wort einfach übersprungen werden, wenn es kein vollständig arabisches Wort ist? Auch `\n` wird als Satzzeichen behandelt -> macht das Sinn?

Ich denke, es sollte ungefähr so funktionieren, dass jeder Text erstmal über ein Pattern in Sätze gesplittet wird und jeder Satz über ein anderes Pattern in Tokens. Dabei merken sich die Sätze und Tokens, was hinter ihnen kommt. Leere Sätze und Tokens werden einfach weggeschmissen. Dann wird für jeden Satz der oben genannte Algorithmus ausgeführt, um die Lemmas und die Wortart zu erhalten. Diese Information helfen dann dabei folgendes zu bestimmen:
- `is_part_of_idafah` (nur Nomen)
- `is_name` (nur Nomen)
- `prefix` (Wort = Präfix + Lemma + Postfix)
- `starts_with_hamzatul_wasl` (nur einige Nomen und Stopwörter und einige Arten von Verben)


> Überspringen Sie den Rest dieses Dokumentes, falls Sie Wichtigeres zu tun haben

# Probleme mit qalsadi und co.

Die Bibliotheken von Taha Zerrouki, die ich im letzten Journal erwähnt hatte sind von ziemlich schlechter Qualität. Der Code ist nicht nur Python 2, sondern ist auch sonst oft unsauber, ineffizient und fehlleitend. Viele Einzelbeispiele lassen schnell darauf schließen. Es werden zum Beispiel Konstanten in Funktionen erstellt, Fehlerüberprüfungen gemacht, die offensichtlich nicht notwendig sind (Längenüberprüfungen nach eine puren Map-Funktion) und scheinbar unnötige Getter, Setter und Debugfunktionen definiert. 

Kommentare und Variablennamen sind außerdem von Rechtschreibfehlern durchzogen. Die Struktur der verschiedenen Bibliotheken und ihre Abhängigkeiten untereinander sind oft nicht klar und es scheint als ob viele Dinge mehrmals implementiert sind, ohne dass klar ist, welche Implementierung die "richtigere" ist. Die Dokumentation ist dahingehend gut, dass Funktionsspezifikationen generell angegeben sind. Es ist jedoch oft nicht das "Warum" klar. 

Es gibt viele Inkonsistenzen. Mal wird zum Cachen ein dict genommen, mal eine pickle DB und mal eine SQLite DB. 

Am meisten Angst machen mir jedoch die TODO-Kommentare -> Irgendetwas ist noch nicht richtig -> Ich muss rausfinden, was nicht richtig ist und es reparieren

## Beispiele 

### Einfache ifs

```py
if word_two in wordtag_const.tab_noun_context \
    or word_two in wordtag_const.tab_noun_context:
    return "t"
```

oder

```py
for char in word:
    # if one char is not a pounct, break
    if char not in POUNCTUATION:
        break
else:
    ...
```

anstatt 

```py
if all(char in PUNCTUATION for char in word):
    ...
```

### Stopwords

`naftawayh` hat zum Beispiel das Modul `ar_stopwords` und das Modul `ar_stowords` mit scheinbar genau dem gleichen Inhalt. Außerdem gibt es das seperate `arabicstopwords` Paket und `tashaphyne` hat auch das Modul `arabicstopwords` und `stopwords`. Zuletzt hat auch `qalsadi` das Modul `stopwords`. 

### Normalize

`tashaphyne` hat das Modul `normalize`, `pyarabic.araby` hat jedoch die meisten Funktionen darin auch implementiert. Diese Funktionen werden dann nochmal in `pyarabic.normalize` in einer Weise reexportiert, dass man meinen könnte, dem Author ginge es nur um die Codezeilen:

```py
import araby as arabconst

...

#strip tatweel from a text and return a result text
#--------------------------------------
def strip_tatweel(text):
    """
    Strip tatweel from a text and return a result text.

    Example:
        >>> text=u"العـــــربية"
        >>> strip_tatweel(text)
        العربية

    @param text: arabic text.
    @type text: unicode.
    @return: return a striped text.
    @rtype: unicode.
    """
    return arabconst.strip_tatweel(text)
```

anstelle von

```py
import araby as arabconst

strip_tatweel = arabconst.strip_tatweel
```

oder vielleicht sogar

```py
from araby import strip_tatweel
```

### WordCase vs. StemmedWord
`qalsadi` hat das Modul `wordcase` mit der Klasse `WordCase` mit der Beschreibung `wordCase represents the data resulted from the morpholocigal analysis` und das Modul `stemmedword` mit der Klasse `StemmedWord` mit der Beschreibung `stemmed_word represents the data resulted from the morpholocigal analysis`. Alles ist lückenlos aber auch sinnlos und nahezu verstörend kommentiert!