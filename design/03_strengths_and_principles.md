# DocNavi – Stärken und Designprinzipien

## Kernidee

DocNavi stellt nicht die generierte KI-Antwort in den Mittelpunkt, sondern die **relevanten Originalfundstellen**.

Prinzip:

**Frage → Fundstellen → Ranking → Original prüfen → optional KI-Text**

## Original first

Die Originalquelle bleibt das maßgebliche Arbeitsobjekt.

DocNavi:

- findet relevante Stellen im Original
- sortiert sie nach Relevanz
- springt direkt zur Fundstelle
- hebt die relevante Passage hervor
- lässt den Benutzer im Original weiterblättern

Die KI ersetzt die Quelle nicht.

## Retrieval first, generation second

Viele KI-Assistenten arbeiten primär so:

**Frage → generierte Antwort → Quellen als Beleg**

DocNavi arbeitet umgekehrt:

**Frage → relevante Quellenstellen → optional kurze KI-Zusammenfassung**

Das reduziert die Abhängigkeit von generierten Aussagen, die plausibel klingen können, aber im Detail falsch sind.

## Human-in-the-loop

Der Benutzer bleibt bewusst im Entscheidungsprozess.

Er kann:

- Fundstellen direkt prüfen
- mehrere Treffer vergleichen
- Kontext vor und nach der Fundstelle lesen
- relevante Stellen auswählen
- KI-Zusammenfassungen gegen das Original kontrollieren

Später kann der Benutzer ausgewählte Originalstellen als Grundlage für ein eigenes Dokument verwenden.

## Mehrdimensionale Relevanz

Ein Treffer erhält nicht nur einen einzelnen Similarity-Score.

Die Relevanz wird auf mehreren Ebenen betrachtet:

- Kapitel
- Unterkapitel
- Absatz
- Satz

Beispiel:

`Kapitel 0,72 | Unterkapitel 0,84 | Absatz 0,93 | Satz 0,89`

Dadurch wird sichtbar, ob eine Stelle nur lokal gut passt oder auch im passenden übergeordneten Kontext steht.

Die Gewichtung der Ebenen soll einstellbar sein.

## Ranked Result List

Die Hauptausgabe ist eine **nach Relevanz sortierte Ergebnisliste**.

Nicht die KI entscheidet, welche Antwort der Benutzer sehen soll. Stattdessen erhält der Benutzer mehrere Kandidaten und kann selbst auswählen.

Das unterstützt:

- Vergleich
- Kontrolle
- Nachvollziehbarkeit
- Exploration des Dokuments

## KISS

DocNavi versucht nicht, aus jeder Frage sofort eine perfekte Antwort zu synthetisieren.

Die Kernaufgabe ist einfacher:

**die richtigen Stellen finden, sinnvoll sortieren und im Original zugänglich machen.**

Komplexere KI-Funktionen können darauf aufbauen, ohne den Kern zu ersetzen.

## Spätere Synthese

Optional kann DocNavi später ausgewählte Originalfundstellen in ein neues Arbeitsdokument übernehmen.

Prinzip:

**Originalstelle auswählen → übernehmen → neues Dokument aufbauen**

Ein LLM kann danach bei Zusammenfassung oder Synthese helfen.

Auch hier bleibt der Mensch im Kontrollprozess.

## Potenzielle Stärke

DocNavi eignet sich besonders für Situationen, in denen **„fast richtig“ nicht ausreicht**.

Der Schwerpunkt liegt deshalb auf:

**Nachvollziehbarkeit, Originalnähe und kontrollierter KI-Unterstützung.**