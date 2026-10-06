# Info Retriever – Low-Level Design

**Status: Entwurf – noch keine Freigabe zur Implementierung.** Benutzerziele und mentales Modell stehen im [HLD](hld.md). Detailentwürfe ergänzen wir hier schrittweise; ein Go gilt für den jeweils vereinbarten Umfang.

## Architektur

```text
Browser: Oberfläche, PDF.js, fetch()
                 ↕ HTTP / JSON, PDF-Datei
api.py: dünne FastAPI-Fassade
                 ↓
service.py: übergreifende Koordination und Zustand
                 ↓
pdf.py · embeddings.py · index.py · search.py
                 ↕ gemeinsame Datenmodelle
models.py
```

Das Backend läuft als lokaler Python-Prozess. Vorgesehen sind Docling für PDF-Analyse, Sentence Transformers mit PyTorch für CPU-Embeddings und FAISS für Vektorsuche. Das konkrete Embedding-Modell ist offen; `multilingual-e5-small` ist ein Kandidat. Keine Browser-Portierung, kein Chat-Modell und keine Agentensteuerung. Frontend und API sollen über denselben lokalen Server erreichbar sein.

## Projektstruktur und Zuständigkeiten

```text
backend/
├── pyproject.toml
├── src/
│   └── info_retriever/
│       ├── __init__.py
│       ├── api.py           # HTTP entgegennehmen, delegieren, antworten
│       ├── service.py       # Abläufe verbinden und gemeinsamen Zustand halten
│       ├── models.py        # Dokumentelemente, Fundstellen, Suchtreffer
│       ├── pdf.py           # PDF laden und strukturieren
│       ├── embeddings.py    # Embedding-Schnittstelle und Modelladapter
│       ├── index.py         # FAISS-Index aufbauen und durchsuchen
│       └── search.py        # Anfrage einbetten und Treffer zusammenstellen
└── tests/
    ├── fixtures/
    ├── test_pdf.py
    ├── test_embeddings.py
    ├── test_index.py
    ├── test_search.py
    ├── test_service.py
    └── integration/         # Reale Komponenten und HTTP-Anbindung
```

Die Fachmodule entsprechen internen Verarbeitungsschritten, nicht jeweils einer eigenen Benutzeraktion. Ihre klare Zuordnung bleibt erhalten. Module und Tests entstehen nach Bedarf; Funktionen genügen, solange Klassen keinen konkreten Vorteil bringen. `pyproject.toml` bündelt Paketdefinition, Abhängigkeiten und Testkonfiguration.

`api.py` kennt FastAPI, prüft HTTP-Eingaben und übersetzt Ergebnisse und Fehler in HTTP-Antworten. Sie delegiert an `service.py` und enthält keine fachliche Ablaufsteuerung oder Zustandsverwaltung. Service und Fachmodule kennen FastAPI nicht; sie sind direkt aus pytest oder einem Notebook aufrufbar. Der Browser lädt eine Datei hoch und verwendet danach eine Dokument-ID, keine frei wählbaren internen Dateipfade.

## Use Cases und interne Verarbeitung

| Benutzer-Use-Case aus dem HLD | Service-Operation (vorgeschlagen) | Interner Ablauf |
|---|---|---|
| UC 1: PDF zum Durchsuchen öffnen | `prepare_document(pdf_path) → DocumentInfo` | `pdf.py`: analysieren und Elemente/Fundstellen ermitteln → `embeddings.py`: Texte einbetten → `index.py`: FAISS-Index aufbauen |
| UC 2: Informationen im PDF suchen | `search(document_id, query, limit) → list[SearchHit]` | An `search.py` delegieren: Query-Embedding → FAISS-Suche → Treffer samt Originaltext und Fundstellen zusammenstellen |
| UC 3: Fundstelle im Original prüfen | `get_document(document_id) → Path` | Original-PDF bereitstellen; Navigation und Markierung anhand der bereits gelieferten Fundstellen übernimmt PDF.js im Frontend |

Ein `InfoRetriever`-Objekt in `service.py` hält Modelladapter, Dokumentelemente und Index für ein aktives PDF. Es verbindet die Schritte; die Verarbeitungsdetails bleiben in den Fachmodulen. Das Modell wird über mehrere Anfragen wiederverwendet. Erst eine vollständig erfolgreiche Aufbereitung stellt das Dokument als durchsuchbar bereit; kein Suchaufruf darf einen halbfertigen Index sehen. Fehler wie unlesbare PDFs, fehlender zugänglicher Text oder unbekannte Dokumente werden verständlich gemeldet.

## Datenmodelle und Originalbezug

`models.py` enthält Python-Darstellungen der fachlichen Daten, keine KI-Modelle:

- **Dokumentelement:** eindeutige ID, Originaltext, Hierarchieebene (Kapitel, Unterkapitel, Absatz, Satz) und gegebenenfalls übergeordnetes Element.
- **Fundstelle:** Seite und Positionsdaten; ein Element kann mehrere Rechtecke auf mehreren Seiten benötigen.
- **Suchtreffer:** Referenz auf das Dokumentelement, Suchscore und zugehörige Fundstellen.

**Indexeintrag → Dokumentelement → Originalfundstelle** bleibt eindeutig. Zusätzlich eingebetteter Kontext wie Überschriften ersetzt nicht den Originaltext. Wiederkehrende Texte und Regelnummern dürfen keine Zuordnung allein über Textgleichheit auslösen. Nicht zuverlässig erkennbare Hierarchie bleibt als Unsicherheit sichtbar.

## Embeddings und FAISS

Der dünne Adapter bietet `embed_documents(texts)` und `embed_query(text)` sowie Modellkennung, Vektordimension und Eingabelimit. Er übernimmt Modellaufruf, Präfixe und Vektornormalisierung. Vorgesehen ist ein kleines Python-`Protocol`; der Adapter wird den verarbeitenden Komponenten übergeben. Tests können feste Vektoren liefern. Ein Plugin-System ist nicht erforderlich.

Dokumentinhalte werden auf mehreren ermittelbaren Hierarchieebenen eingebettet. Lange Abschnitte dürfen nicht stillschweigend abgeschnitten werden; ihre Behandlung ist noch zu entwerfen. Query und Dokument müssen mit kompatiblen Modell- und Verarbeitungseinstellungen eingebettet werden. Ein Modellwechsel erfordert neue Dokument-Embeddings und einen neuen Index.

`index.py` kapselt FAISS und die Zuordnung der Vektoren zu Elementen. Als einfacher Start ist exakte Suche mit `IndexFlatIP` über normalisierte Vektoren vorgesehen; das Skalarprodukt entspricht dann der Cosine Similarity. Die Zusammenführung von Treffern verschiedener Ebenen bleibt offen. Eine einstellbare mehrdimensionale Gewichtung gehört nicht zum MVP.

## Tests und Experimente

Es gelten [AGENTS.md](../AGENTS.md) und die dort eingeordneten [Testregeln](how_to_test.md). Unit-Tests orientieren sich an den Fachmodulen und prüfen beobachtbares Verhalten; keine Pflichttests für private Hilfsfunktionen oder triviale Weiterleitungen. Integrationstests liegen unter `tests/integration`.

- Kleine PDFs prüfen Extraktion, Hierarchie und Fundstellen, insbesondere ähnlich formulierte Abschnitte mit unterschiedlichen Überschriften.
- Feste Vektoren prüfen Ranking und Zuordnung; Integrationstests verwenden echtes FAISS und reale PDF-Verarbeitung. Service-Tests prüfen Abläufe und Zustandswechsel bei Erfolg und Fehlern.
- Tests mit echtem Embedding-Modell laufen gesondert; schnelle Tests benötigen keinen Modelldownload. HTTP-Verhalten wird mit pytest und FastAPIs `TestClient` ohne separat gestarteten Webserver geprüft.
- Suchqualität wird mit echten Fragen und erwarteten Fundstellen beurteilt, zunächst an der BDS-IPSC-Sportordnung. Viewer-Tests prüfen später Navigation und Markierung einschließlich Zoom und Seitengeometrie.

Zur Fehlersuche dienen Python-Debugger und Browser-DevTools; eine optionale Detailanzeige kann Seite, Element-ID und Suchscore sichtbar machen. Ein Score erklärt dabei keine fachliche Gültigkeit.

## Nächste Detailentwürfe und Freigaben

Noch kein Implementierungsschritt ist freigegeben. Zuerst entwickeln und testen wir den Python-Kern, danach die HTTP-Anbindung und später das Frontend. Die folgenden Punkte werden vor dem jeweils betroffenen Schritt konkretisiert:

| Bereich | Offen |
|---|---|
| PDF-Aufbereitung | Docling-Einsatz, Hierarchieerkennung, Satzzerlegung, Seitenzählung und Koordinatenkonvention |
| Embeddings | Startmodell und Behandlung langer Abschnitte auf mehreren Ebenen |
| Index | Lebensdauer; gegebenenfalls dauerhafte Speicherung mit Modell- und Verarbeitungskennung |
| Suche | Zusammenführung verschiedener Ebenen und überlappender Treffer |
| Service und HTTP | Dokumentwechsel, parallele Aufrufe, Upload-Lebensdauer, längere Verarbeitung und Fortschritt, Request-/Response-Typen und Fehlerfälle |
| Frontend | Übergabe der Markierungsdaten und Zusammenspiel mit dem Viewer |

Für jeden Schritt ergänzen wir nur die nötigen Details, Tests und den Status: Entwurf → freigegeben → umgesetzt.
