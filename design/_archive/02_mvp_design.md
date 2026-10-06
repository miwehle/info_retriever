# DocNavi – MVP Design

## Ziel

Schnell einen funktionierenden Prototyp bauen, um den Nutzen von DocNavi praktisch zu prüfen.

Keine Browser-Extension im MVP, sondern zunächst eine lokale Web-Anwendung.

## Komponenten-Architektur

**Browser-Frontend**

↕ HTTP / JSON

**Python-Backend**

→ Docling  
→ Sentence Transformers  
→ Ranking

Optional später:

→ FAISS  
→ LLM  
→ OCR

## Browser-Frontend

Aufgaben:

- PDF mit **PDF.js** anzeigen
- Suchfeld bereitstellen
- Result List anzeigen
- Treffer auswählen
- zur Fundstelle springen
- relevante Textstelle hervorheben
- Debug-Informationen zu Treffern anzeigen

Die KI-Seitenleiste besteht aus:

- Suchfeld
- Result List

## Python-Backend

Aufgaben:

- PDF mit **Docling** analysieren
- Dokumentstruktur extrahieren
- Absätze und Sätze bestimmen
- Embeddings mit **Sentence Transformers** berechnen
- Query-Embedding erzeugen
- Ähnlichkeiten berechnen
- Treffer sortieren
- Ergebnisse an das Frontend liefern

Im MVP reicht direkte **Cosine Similarity**. FAISS ist zunächst nicht nötig.

## Datenfluss

`PDF`

→ Docling  
→ Dokumentelemente  
→ Sentence Transformers  
→ Embeddings

`Suchanfrage`

→ Query-Embedding  
→ Cosine Similarity  
→ Ranking  
→ Result List  
→ Auswahl eines Treffers  
→ PDF.js springt zur Fundstelle

## Debugging

### Python

- VS Code Debugger
- Breakpoints
- Variableninspektion
- automatisierte Tests mit **pytest**

Zu testen sind insbesondere:

- Dokumentstruktur
- Zerlegung in Absätze und Sätze
- Embedding-Erzeugung
- Ähnlichkeitsberechnung
- Ranking
- spätere Gewichtung mehrerer Hierarchieebenen

### Browser

Chrome/Edge DevTools:

- JavaScript-Debugging
- DOM
- Network Requests
- PDF.js-Verhalten

Zusätzlich soll die Result List optional Debug-Werte anzeigen, z. B.:

`page=37 | paragraph=12 | similarity=0.87`

Damit ist direkt sichtbar, warum ein Treffer seine Position erhält.

## MVP-Funktionsumfang

- textbasierte PDFs
- lokale Web-Anwendung
- PDF.js
- Docling
- Sentence Transformers
- Cosine Similarity
- Suchfeld
- sortierte Result List
- Klick auf Treffer
- Navigation zur Fundstelle
- Hervorhebung der relevanten Passage
- pytest für die Logik

Nicht im MVP:

- Browser-Extension
- OCR
- FAISS
- LLM-Zusammenfassungen
- Markdown-/HTML-Ordner
- aufwendige Up-front-Architektur
