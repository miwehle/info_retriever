# KI-Agent für PDF-Dateien

## Ziel

Browserbasierte Anwendung zur semantischen Suche in textbasierten PDF-Dokumenten.

Der Benutzer stellt eine Frage oder Suchanfrage. Die Anwendung findet relevante Stellen im Dokument, bewertet deren Relevanz und zeigt die ausgewählte Stelle direkt im PDF an.

## Mentales Modell des Frontends

```
Browser-Tab
┌─────────────────────────────────────────────────────────────────┐
│ Info Retriever                                                  │
├──────────────────────────────────┬──────────────────────────────┤
│ PDF-Viewer                       │ KI-Seitenleiste              │
│                                  │                              │
│ Seite 37                         │ Suchfeld                     │
│ ┌──────────────────────────────┐ │ ┌──────────────────────────┐ │
│ │                              │ │ │ Wie funktioniert ... ?   │ │
│ │ Text ...                     │ │ └──────────────────────────┘ │
│ │                              │ │                              │
│ │ █ relevante Passage █       │ │ Ergebnisliste / RRL         │
│ │                              │ │                              │
│ │ weiterer Text ...            │ │ 1. Treffer                  │
│ │                              │ │    Kapitel      ████████    │
│ └──────────────────────────────┘ │    Unterkapitel ███████     │
│                                  │    Absatz       █████████   │
│ Seite 36  ←  37  →  Seite 38    │    Satz         ██████████  │
│                                  │                              │
│                                  │ 2. Treffer                  │
│                                  │    ...                       │
└──────────────────────────────────┴──────────────────────────────┘

Auswahl eines Treffers
        ↓
PDF-Viewer springt zur Fundstelle
        ↓
relevante Passage wird hervorgehoben
```
## Oberfläche

Die Anwendung besteht aus zwei Hauptbereichen:

- **PDF-Viewer**
- **KI-Seitenleiste**

### PDF-Viewer

Aufgaben:

- PDF anzeigen
- normales Blättern im Dokument
- zu einer gefundenen Stelle springen
- relevante Textpassagen hervorheben
- Text auswählen und kopieren

Als technische Basis bietet sich **Mozilla PDF.js** an.

### KI-Seitenleiste

Besteht aus:

- **Suchfeld**
- **Ergebnisliste / Result List**

## Ergebnisliste

Die Ergebnisliste enthält mehrere zur Suchanfrage passende Dokumentstellen.

Eigenschaften:

- Ergebnisse sind nach Relevanz sortiert.
- Ein Ergebnis kann ausgewählt werden.
- Der PDF-Viewer springt daraufhin zur entsprechenden Stelle.
- Die relevante Textpassage wird im PDF hervorgehoben.
- Zu jedem Ergebnis kann eine kurze, auf die Suchanfrage bezogene Zusammenfassung angezeigt werden.

### Relevanz

Die Relevanz eines Ergebnisses wird auf mehreren Ebenen betrachtet:

- Kapitel
- Unterkapitel
- Absatz
- Satz

Für jede Ebene wird ein eigener Relevanzwert berechnet.

Die Gewichtung dieser vier Werte soll vom Benutzer einstellbar sein.

Beispiel:

`Gesamtscore = wK·Kapitel + wU·Unterkapitel + wA·Absatz + wS·Satz`

Die Ergebnisliste wird nach diesem Gesamtscore sortiert.

Technischer Begriff:

**Ranked Result List (RRL)**

## Dokumentstruktur

Wenn das PDF bereits strukturiert ist, kann diese Struktur direkt verwendet werden.

Bei normalen textbasierten PDFs soll die Struktur automatisch rekonstruiert werden:

- Kapitel
- Unterkapitel
- Absätze
- Sätze

Für die Dokumentanalyse bietet sich **Docling** an.

OCR ist zunächst nicht vorgesehen. Unterstützt werden zunächst PDFs, deren Text direkt zugänglich ist.

## Semantische Suche

Für jedes relevante Dokumentelement wird ein Embedding berechnet:

- Kapitel
- Unterkapitel
- Absatz
- Satz

Auch die Suchanfrage erhält ein Embedding.

Die Ähnlichkeit zwischen Suchanfrage und Dokumentelementen bestimmt die jeweiligen Relevanzwerte.

Geeignet dafür:

**Sentence Transformers**

Die Modelle können lokal über Python/PyTorch ausgeführt werden. Kleine Embedding-Modelle benötigen keine GPU.

## Vektorsuche

Für größere Mengen von Embeddings kann **FAISS** eingesetzt werden.

FAISS:

- steht für **Facebook AI Similarity Search**
- stammt von Facebook AI Research / Meta
- läuft lokal
- ist Open Source
- benötigt für diesen Anwendungsfall keine GPU

Für einen ersten Prototyp ist FAISS nicht zwingend notwendig. Bei einem einzelnen PDF können die Embeddings auch direkt per Cosine Similarity verglichen werden.

## Vorläufiger technischer Stack

**PDF.js**

→ PDF-Anzeige, Navigation, Textauswahl, Hervorhebung

**Docling**

→ Dokumentstruktur und Textblöcke

**Sentence Transformers**

→ Embeddings für Suchanfrage und Dokumentelemente

**FAISS**

→ optionaler Index für schnelle Vektorsuche

**LLM**

→ optional für kurze, auf die Suchanfrage bezogene Zusammenfassungen

## Grober Ablauf

`PDF`

→ Docling analysiert Dokumentstruktur

→ Kapitel, Unterkapitel, Absätze und Sätze werden extrahiert

→ Sentence Transformers erzeugt Embeddings

→ Benutzer gibt Suchanfrage ein

→ Query-Embedding wird erzeugt

→ Ähnlichkeiten werden berechnet

→ gewichteter Gesamtscore wird bestimmt

→ Ranked Result List wird erzeugt

→ Benutzer wählt Ergebnis

→ PDF.js springt zur Stelle und hebt sie hervor

## MVP

Für eine erste Version:

- nur textbasierte PDFs
- PDF.js
- Docling
- Sentence Transformers
- direkte Cosine Similarity
- Kapitel / Unterkapitel / Absatz / Satz
- gewichtete Ergebnisliste
- Klick auf Ergebnis → Sprung zur markierten Stelle im PDF

FAISS, OCR und zusätzliche LLM-Funktionen können später ergänzt werden.