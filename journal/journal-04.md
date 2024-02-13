# Transliteration

In dieser Woche will ich mich insbesondere mit der Transliteration beschäftigen. Dazu gibt es drei Themen, die ich konkret angehen möchte:

- Tokenisierung
- Präfixbestimmung
- Idafah

## Tokenisierung

Ich möchte gerne meinen eigenen Tokenisierungsalgorithmus benutzen:

- Im Allgemeinen sollte jeder Text in Sätze aufgeteilt werden und jeder Satz in Tokens (im Endeffekt eine zusammenhängende Folge von Buchstaben). 
- Um den Originaltext einfach wiederherstellen zu können, sollten die Tokens immer speichern, was zwischen ihnen liegt.
- Es gibt für die Tokenisierung grob gesagt drei Arten von Charakteren: Leerzeichen (insbesondere " " und "\n"), Satzzeichen (insbesondere ".", "!", "?", "," und deren arabische Äquivalente) und zuletzt alles andere also Buchstaben. Zusätzlich könnte man noch Emojis unterscheiden und in unserem Fall kann man wahrscheinlich auch nicht-arabische Zeichen trennen.

### Satzzeichen
Es gibt nun für Satzzeichen drei Ansätze:
1. Man kann die Satzzeichen als Teil eines vorhergehenden Tokens betrachten
2. Man kann den Satzzeichen ein eigenes Token geben
3. Man kann die Satzzeichen so wie Leerzeichen behandeln und nicht als Teil von Tokens betrachten

\1. macht in diesem Fall keinen Sinn, da wir uns oft auch den letzten Buchstaben anschauen wollen, und Satzzeichen dann und auch sonst einfach stören. 2. scheint mir einfach aufwendiger ist aber auch ein valide Option. Ich habe mich jedoch schlussendlich für 3. entschieden, weil es wahrscheinlich am einfachsten zu implementieren ist.

### Was ist ein Token? oder Was ist kein Token?

~~Für mich sind Tokens in der Sprache der regulären Ausdrucke sehr einfach Buchstaben zwischen Wortgrenzen: [`\b\w+\b`](regexr.com/7rtn8). Die Wortgrenzen sind jedoch nicht notwendig. Ich vertraue hier darauf, dass die Regex-Engine Unicode Arabisch unterstützt. Andernfalls, könnte man auch erwarten, dass ein User einen rein arabischen Text eingibt und ein Pattern nutzen wie `rf"[{arabic_letters}]+"`, wobei `arabic_letters` ein String mit allen arabischen Buchstaben ist.~~

Das Regex ist nun (mit Abischt auf Erweiterung) auf `"[\u0621-\u0655]+"` gefallen, da `\w+` nicht ausreichend war. Siehe den [Unicode Arabischblock](https://en.wikipedia.org/wiki/Arabic_(Unicode_block)) für einen besseren Überblick. 

### Pseudocode

```py
TOKEN_PATTERN = re.compile("w+")

def tokenize(text: str)->list[list[Token]]:
    # Der Rest des Algorithmusses geht davon aus, dass es immer mindestens ein Token gibt!
    text = text.strip()
    if not text:
        return ""
    # Falls eine Frontend-Cache angewandt werden soll, dann könnte das Frontend die Schritte bis hier auch schon durchführen.
    tokens, ends, starts = zip(
        *(token, match.end(), match.start())
        for match in TOKEN_PATTERN.finditer(text)
        if (token:=text[match.start(): match.end()])
    )
    # um ganz sicher zu gehen: "."
    if not tokens:
        return ""
    # Der Start des nächsten Tokens ist das Ende des Anhängsels des jetzigen Tokens
    # Beim letzten Token ist das Ende des Anhängsels das Ende des Textes
    starts = [
        *starts[1:],
        len(text)
    ]
    tokens = [
        Token(token, after=text[end:start]) for token, end, start in zip(tokens, ends, starts)
    ]
    for token in tokens:
        # Dieser Teil könnte übrigens auch Teil der Tokeninitialisierung sein
        token.lemma, token.pos, token.prefix, *anything_else_we_might_need! = get_token_info(token)
        # has hamzatul wasl???

    sentences = []
    current_sentence = []
    for token in tokens:
        current_sentence.append(token)
        # stop marks sind insbesondere "." und "\n"
        if any(c in token.after for c in sentence_stop_marks):
            sentences.append(current_sentence)
            current_sentence = []
    if current_sentence:
        sentences.append(current_sentence)

    # Hier wird klar, wieso wir überhaupt Sätze verwenden
    for sentence in sentences:
        # idafah
        for token, next_token in zip(sentence, sentence[1:]):
            token.is_idafah = (
                token.is_genetive 
                and next_token.pos == "noun" 
                and next_token.prefix not in preposition_prefixes
            )
        # pausa beim letzten Wort des Satzes
        sentence[-1].pausa = True

    return sentences   
```

## Wortarten

Wie werden verschiedene Wortarten gepostaggt (Neozismus):
- nouns
    - Nomen
    - Adjektive
- verbs:
    - Verben

Der Rest gibt unklare Ergebnisse

## Ergebnis bisher

Ich habe die Transliterierung mit ein wenig copy-paste nochmal ganz von vorne in einem viel weniger objekt-orientierten und viel mehr imperativem Stil. Es gibt also nur eine einzige Funktion, die im Endeffekt alles macht. Der endgültige Code sieht im Endeffekt so aus, wie oben angegeben, aber natürlich konkreter. Bisher funktioniert die Transliteration ganz gut für einfache teil-vokalisierte Sätze. 

Ich habe entdeckt, dass Qalsadi auch schon automatisch zumindest zu einem gewissen Grad vokalisieren kann. Ich habe mich auf diese Fähigkeit jedoch nicht besonders verlassen.

Leider musste ich feststellen, dass der Tagger einige recht häufige Wörter nicht erkennen konnte und dementsprechend auch nicht postaggen konnte, was ich eigentlich erwartet hätte. Das liegt möglicherweise daran, dass ich einen Teil des Wörterbuches (der in SQLite lief) ausgeschaltet habe.
