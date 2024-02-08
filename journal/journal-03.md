

> Überspringen Sie den Rest dieses Dokumentes, falls Sie Wichtigeres zu tun haben

# Probleme mit qalsadi und co.

Die Bibliotheken von Taha Zerrouki, die ich im letzten Journal erwähnt hatte sind von extrem schlechter Qualität. Der Code ist nicht nur Python 2, sondern ist auch sonst oft unsauber, ineffizient und fehlleitend. Viele Einzelbeispiele lassen schnell darauf schließen. Es werden zum Beispiel Konstanten in Funktionen erstellt, Fehlerüberprüfungen gemacht, die offensichtlich nicht notwendig sind (Längenüberprüfungen nach eine puren Map-Funktion) und scheinbar unnötige Getter, Setter und Debugfunktionen definiert. 

Kommentare und Variablennamen sind außerdem von Rechtschreibfehlern durchzogen. Die Struktur der verschiedenen Bibliotheken und ihre Abhängigkeiten untereinander sind oft nicht klar und es scheint als ob viele Dinge mehrmals implementiert sind, ohne dass klar ist, welche Implementierung die "richtigere" ist. Die Dokumentation ist dahingehend gut, dass Funktionsspezifikationen generell angegeben sind. Es ist jedoch oft nicht das "Warum" klar. 

Es gibt viele Inkonsistenzen. Mal wird zum Cachen ein dict genommen, mal eine pickle DB und mal eine SQLite DB. 

## Beispiele 

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