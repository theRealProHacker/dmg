# Was bisher geschah ...

Bisher wurde die DMG Transliteration nach Spezifikation minimal implementiert. Die Sonnenbuchstabenassimilation funktioniert zum Beispiel schon mal. Auch das Konzept eines Profils, mit dem eingestellt werden kann, wie genau die Transliteration ablaufen soll, wurde schon eingeführt. Es gibt jedoch noch keine UI.

# Allgemeine Gedanken

## Das Profil

Wie gesagt gibt es das Konzept eines Profils schon. Es fehlt mir jedoch noch die Einsicht, um ein abschließendes Ergebnis darzulegen. Das ist der nächste Schritt, den ich mit einem Experten durchsprechen muss.

## Das UI

Als UI stell ich mir eine Eingabe- und eine Ausgabetextbox vor, die im horizontalen Layout nebeneinander stehen und im vertikalen übereinander. Dabei macht es Sinn die westliche Ausrichting zu wählen, bei dem die Eingabe links/oben steht und die Ausgabe rechts/unten. Ich stell mir dazu eine Sidebar vor, die auf- und zugeklappt werden kann und in der das Profil bestimmt werden kann. 

Immer wenn entweder das Profil umgestellt oder der Eingabetext bearbeitet wird und daraufhin für einige Sekunden nicht mehr editiert wird, dann kann eine POST-Anfrage (s. (HTTP POST)[https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST]) mit dem Eingabetext und dem Profil als Payload geschickt werden. 

Für einen einheitlichen Stil und die erwähnten Komponenten scheint Bootstrap sinnvoll. Ich bin damit vertraut und es wird die Prototypisierung sehr viel einfacher machen.

Als Arabischfont bietet sich [Noto Naskh Arabic](https://fonts.google.com/noto/specimen/Noto+Naskh+Arabic) an.

### Hosting

Eine einfache Alternative ist zum Beispiel pythonanywhere. ~~Ich habe mich dafür entschieden, [diesem Tutorial](https://www.youtube.com/watch?v=1FdrJPt77GU) zu folgen und [Zeet](https://zeet.co/r/thecodex) zu verwenden.~~

### Weiterführende Gedanken

Ob Clientside Caching sinnvoll ist, ist fraglich. Es könnte zum Beispiel helfen, wenn ein User bei dem Profil ein boolean wiederholt hin und her wechselt. Dann könnte der Client die Useranfrage sofort bedienen. Dazu könnte man zum Beispiel auch die HTTP-Cache des Clients "missbrauchen".

Serverside Caching ist sinnvoll, falls Anfragen rechenintensiv sind, was bisher nicht der Fall ist. Dann sollte die Transliteration auch nicht automatisch nach kurzer Inaktivität geschehen, sondern explizit bestätigt werden, um unnötige Berechnungen zu vermeiden.

Langfristig sollte es möglich sein aus einer Liste von voreingestellten Profilen auszusuchen und diese auch selbst zu editieren oder neue zu erstellen. 

# Transliterationsspezifische Gedanken

## Dialekte

Ich habe mir überlegt, dass die Implementierung für verschiedene Dialekte den Rahmen der Arbeit sprengen würde. Trotzdem möchte ich den Usecase in Betracht ziehen, dass jemand ein Dialekt transliterieren möchte und daher den Ein- oder Ausgabetext möglicherweise auch während des Transliterationsprozesses editieren muss. 

Beispielsweise könnte ein User den Ausgabetext *S* eines Eingabetexts *T* zu *S\** editieren, dann aber den Eingabetext doch noch zu *T'* ändern. Dann sollte der Ausgabetext *S'* im optimalen Fall trotzdem noch *S\** in Betracht ziehen!

Das ist jedoch ein sehr schwieriges Unterfangen mit im Endeffekt immer noch relativ wenig Nutzen. 

## Das Ta' marbutah

Das Ta' marbutah kommt nur am Ende von (grammatikalisch) femininen Substantiven, Adjektiven und Partizipien vor. Es ist einer der schwierigeren Buchstaben zu transliterieren. Es gibt drei Möglichkeiten, wie es, der Aussprache entsprechend, transliteriert wird: als "h", als "t" oder gar nicht "".

### Die Idafah

Mit meinem jetzigen Verständnis wird das Ta' marbutah genau dann zu einem "t", wenn das Wort in einer Genetivverbindung *Idafah* steht. Das ist genau dann der Fall, wenn das darauffolgende Wort (außer Adjektiv) im Genetiv steht. Dies wiederum wird durch eine finale *Kasra* (Kurzvokal "i") gekennzeichnet. Um also eine Idafah zu bestimmen, muss lediglich gecheckt werden, welche Wortart das nächste Wort hat und welches finale Zeichen es hat. 

Es gibt noch eine kleine Sache, die zu beachten ist. Wenn nämlich das darauffolgende Wort eine präfixierte Präposition enthält, dann wird es immer im Genetiv stehen, ohne dass eine Idafah besteht. 

### Sonst

In jedem anderen Fall wird es entweder als "h" oder nicht transliteriert. 

Wenn vor dem Ta' marbutah ein langer Vokal steht (alif, ya', waw, ā, ū, ī) oder das Ta' marbutah nicht der letzte Buchstabe ist, dann wird es als "h" transliteriert, sonst darf man es sich aussuchen. Theoretisch könnte man sich von Fall zu Fall anders entscheiden, aber ich habe mich dazu entschieden, diese Option global im Profil für den ganzen Text zu setzen. 

## Einzelne Buchstaben

Eine Frage ist noch, wie einzelne Buchstaben transliteriert werden. Einmal könnte man nur den Buchstaben alleine transliterieren: "b", "y". Dann müsste man sich noch um Ausnahmen wie Hamzah oder Ta' marbutah kümmern. Andernfalls könnte man die Langform transliterieren: "Bāʾ", "Yāʾ". Diese Frage könnte man im Profil natürlich auch wieder auf den User übertragen. 

## Hamzatul wasl

Das Hamzatul wasl ist ein Hamzah, das mitsamt Kurzvokal übersprungen wird, wenn man "durch es durch" spricht bzw. wenn man nicht damit anfängt. Ich kann es leider nicht besser erklären. 

In dem folgenden Beispiel sehen wir, dass der Artikel ein Hamzatul wasl enthält. Daher wird es mitsamt des "a" übersprungen, wenn man nicht in Pausa liest. Das Ta' marbutah in *madīnah* wird übrigens immer als "t" gelesen, weil hier eine Idafah besteht. 

Arabisch: مَدينَةُ القاهِرَة
Pausa: madīnat al-qāhira
Normal: madinatu l-qahira

Das Problem mit dem Hamzatul wasl ist, dass es im Schriftbild nicht von dem "gewöhnlichen" Hamzah (Hamzatul Qat) unterschieden wird. Man muss also irgendwie rausfinden, ob ein Hamzah ein Hamzatul wasl ist. Dabei gibt es bei meinem jetzigen Kenntnisstand drei Fälle. Zum Glück reicht es für jedes Wort einfach zu bestimmen, ob es mit einem Hamzatul wasl anfängt, denn ein Hamzatul wasl inmitten eines Wortes existiert nicht.

1. Der Artikel trägt immer ein Hamzatul wasl
2. Es gibt eine begrenzte Anzahl von gewöhnlichen Wörtern (Lemmas), die ein Hamzatul wasl beinhalten (z.B. ism "Name").
3. Zusätzlich gibt es einige Verbtypen, die ein Hamzatul wasl tragen. Diese können an ihrer Form erkannt werden. Um das genau zu verstehen, muss man verstehen, dass quasi jedes arabische Wort aus drei Radikalen bestehen, die die Grundbedeutung vorgeben und einer Form, die diese Grundbedeutung auf eine bestimmte Weise verändert und dabei auch die Wortart bestimmt. Die Flexion wird dann zusätzlich darauf angewandt. Von 10 möglichen Verbformen haben die vier Stämme 7, 8, 9 und 10 bei manchen Konjugationen ein Hamzatul wasl am Anfang. 

In der Implementierung kann der Artikel explizit gehandhabt werden. Der Rest kann als Attribut des Wortes dargestellt werden. 

# Offenes

- Vollständiges Profil, das alle möglichen Präferenzen komplett abdeckt und einfach zu verstehen ist.
- Ist mein Verständnis über die Transliteration des Ta' marbutah, die Definition der Idafah und das Hamzatul wasl korrekt?
- Wie genau können die Stämme 7, 8, 9 und 10 klar erkannt werden.
- Wie sollten einzelne Buchstaben transliteriert werden?