# DocNavi – Formatunabhängigkeit und EPUB

## Formatunabhängiger Kern

DocNavi ist konzeptionell nicht an PDF gebunden.

Der Kern bleibt gleich:

**Dokument → Struktur → Embeddings → Ranking → Originalfundstelle**

Formatspezifisch sind im Wesentlichen nur:

- Parser / Strukturerkennung
- Viewer / Darstellung

Mögliche Formate:

- PDF
- Markdown
- HTML
- DOCX
- EPUB
- Jupyter Notebooks
- LaTeX

## EPUB

EPUB eignet sich besonders gut, weil Kapitel und Unterkapitel meist bereits strukturiert vorliegen.

Ein mögliches Retrieval-Modell:

### 1. Grobsuche

Dauerhafter Index über:

- Buch
- Kapitel
- Unterkapitel
- Titel
- optional Kurzbeschreibung / Zusammenfassung

Die Suchanfrage liefert z. B. die relevantesten 20–100 Kapitel oder Unterkapitel.

### 2. Feinsuche

Nur innerhalb dieser Kandidaten werden anschließend:

- Absätze
- Sätze

extrahiert, eingebettet und gerankt.

Ergebnis:

**Frage → relevante Kapitel → relevante Absätze/Sätze → Originalstelle im EPUB**

## Vorteil

Die zweistufige Suche vermeidet einen sehr großen globalen Satz- und Absatzindex.

Sie passt gleichzeitig gut zum hierarchischen Grundprinzip von DocNavi:

**coarse retrieval → fine retrieval**

Damit lässt sich DocNavi später auch auf große Dokumentbestände und Bibliotheken skalieren.