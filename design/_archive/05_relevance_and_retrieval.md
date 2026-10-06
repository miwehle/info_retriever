# ResourceRetriever – Relevanz, Rückfragen und Coarse-to-Fine Retrieval

## Allgemeines Retrieval-Modell

ResourceRetriever arbeitet nicht nur mit Dokumenten, sondern mit unterschiedlichen Ressourcentypen, z. B.:

- Dokumente
- KI-Modelle
- Software-Libraries
- Datensätze
- wissenschaftliche Papers

Jeder Ressourcentyp besitzt passende **Relevanzdimensionen**.

Beispiele:

**Dokumente**

`Kapitel | Unterkapitel | Absatz | Satz`

**KI-Modelle**

`Task-Fit | Hardware-Fit | Lizenz-Fit | Modellgröße | Aktualität | Qualität`

**Software-Libraries**

`Funktions-Fit | Sprache | Plattform-Fit | Lizenz | Aktualität | Wartungszustand | Abhängigkeiten`

Die Gewichtung dieser Dimensionen kann der Benutzer beeinflussen.

## Relevanz-Vektor

Eine Ressource wird nicht nur mit einem einzelnen Score bewertet, sondern mit einem **Relevanz-Vektor**.

Beispiel:

`Task-Fit 0,94 | Hardware-Fit 0,72 | Lizenz-Fit 1,00 | Aktualität 0,61`

Daraus entsteht über Benutzergewichte ein Gesamtscore für die Ranked Result List.

## Warum?

Jede Relevanzdimension kann bei Bedarf begründet werden:

`Hardware-Fit 0,82  [Warum?]`

Die Begründung sollte möglichst evidenzbasiert sein:

- API-Metadaten
- Model Cards / README / Dokumentstellen
- Benchmarks
- explizite Regeln und Ableitungen
- semantische Ähnlichkeit
- optional kurze LLM-Erklärung

Prinzip:

**Score → Evidenz → optional Erklärung**

## Rolle des Chat-Modells

Das Chat-Modell interpretiert die natürliche Anfrage und überführt sie in einen vorläufigen Relevanz-Vektor.

Es kann:

- Anforderungen erkennen
- unbekannte Dimensionen markieren
- Widersprüche erkennen
- gezielte Rückfragen formulieren
- Antworten wieder in den Relevanz-Vektor einarbeiten

Das Modell soll nicht mechanisch alle Leerstellen abfragen.

## Intelligente Rückfragen

Rückfragen sollen vor allem dort gestellt werden, wo zusätzliche Information das Ranking voraussichtlich stark verbessert.

Dazu betrachtet das System:

- die Anfrage
- den unvollständigen Relevanz-Vektor
- die aktuellen Top-K-Suchergebnisse
- deren Embeddings, Scores und Metadaten

Beispiel:

Wenn sich die Top-Modelle hauptsächlich beim VRAM-Bedarf unterscheiden, ist

> Welche Hardware steht zur Verfügung?

eine bessere Rückfrage als eine Frage zur Aktualität.

Prinzip:

**Ask only when it matters.**

## Suchergebnisse als Grundlage für Rückfragen

Die Embeddings und Merkmale der aktuellen Kandidaten dienen nicht nur dem Ranking, sondern auch der Entscheidung, **welche Rückfrage am meisten Informationsgewinn bringt**.

Ablauf:

**Query → vorläufiges Retrieval → Top-K analysieren → gezielte Rückfrage → verbessertes Retrieval**

## Coarse-to-Fine Retrieval

ResourceRetriever kann große Suchräume zweistufig durchsuchen.

### 1. Grob-Retrieval

Viele Kandidaten werden schnell mit:

- Embeddings
- Metadaten
- Relevanzdimensionen

eingeschränkt.

### 2. Feinprüfung

Bei kleiner Kandidatenmenge wird direkt in die Ressourcen geschaut.

Beispiele:

- PDF: Kapitel → Absatz → Satz
- KI-Modell: Model Card, Config, Benchmarks
- Library: README, API-Doku, Releases, Issues
- Paper: Abstract, Methoden, Ergebnisse

Danach kann das System:

- feiner re-ranken
- weitere Evidenz sammeln
- gezielter nachfragen

## Human-in-the-loop

Der Mensch bleibt an mehreren Stellen beteiligt:

- formuliert die Anforderung
- gewichtet Relevanzdimensionen
- beantwortet gezielte Rückfragen
- kann über **Warum?** Evidenz einsehen
- prüft und wählt aus der Ranked Result List

Das Ziel ist keine vollständige Black-Box-Vermeidung, sondern **mehr Transparenz durch verständliche Relevanzdimensionen, sichtbare Evidenz und kontrollierte Interaktion**.
