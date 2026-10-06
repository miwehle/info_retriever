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
                 ↓ bei KI-Operationen
ai.py: allgemeine KI- und Vektorsuchoperationen
                 ↓
Embedding-Bibliothek · FAISS

models.py: gemeinsame fachliche Datenmodelle
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
│       ├── embeddings.py    # Dokumentelemente und Kontext zum Einbetten aufbereiten
│       ├── index.py         # Dokumentindex und Zuordnung zu Elementen aufbauen
│       ├── search.py        # Anfrage aufbereiten und fachliche Treffer zusammenstellen
│       └── ai.py            # Modelladapter, Embeddings und Vektorsuche kapseln
└── tests/
    ├── fixtures/
    ├── test_pdf.py
    ├── test_embeddings.py
    ├── test_index.py
    ├── test_search.py
    ├── test_service.py
    ├── test_ai.py
    └── integration/         # Reale Komponenten und HTTP-Anbindung
```

Die Fachmodule entsprechen internen Verarbeitungsschritten, nicht jeweils einer eigenen Benutzeraktion. Ihre klare Zuordnung bleibt erhalten. Module und Tests entstehen nach Bedarf; Funktionen genügen, solange Klassen keinen konkreten Vorteil bringen. `pyproject.toml` bündelt Paketdefinition, Abhängigkeiten und Testkonfiguration.

`api.py` kennt FastAPI, prüft HTTP-Eingaben und übersetzt Ergebnisse und Fehler in HTTP-Antworten. Sie delegiert an `service.py` und enthält keine fachliche Ablaufsteuerung oder Zustandsverwaltung. Service und Fachmodule kennen FastAPI nicht; sie sind direkt aus pytest oder einem Notebook aufrufbar. Der Browser lädt eine Datei hoch und verwendet danach eine Dokument-ID, keine frei wählbaren internen Dateipfade.

**Abhängigkeitsregel:** Im Produktionscode dürfen FastAPI-Imports und die Verwendung seiner Funktionen, Decorators und Typen ausschließlich in `api.py` stehen. Tests der HTTP-Anbindung dürfen FastAPIs `TestClient` verwenden.

Diese Grenze soll einen späteren Austausch von FastAPI auf die HTTP-Anbindung und deren Tests begrenzen; Service und Fachmodule bleiben bei unverändertem Schnittstellenvertrag unberührt. Ein alternatives Framework oder zusätzliche Abstraktionen dafür führen wir erst bei konkretem Bedarf ein.

## KI-Fassade und Vektorsuche

`ai.py` kapselt allgemeine KI-Operationen; im Produktionscode stehen ausschließlich dort die Imports und Aufrufe der verwendeten KI-Tools. Die Funktionen delegieren meist mit wenigen Zeilen und vereinheitlichen bei Bedarf Präfixe, Zahlenformate und Normalisierung. Die Schnittstelle arbeitet mit Texten, Vektoren und neutralen IDs; Dokumentelemente, Kontextauswahl, Fundstellen und Trefferaufbereitung bleiben in den Fachmodulen.

- **Embeddings:** `embed_documents(texts)` und `embed_query(text)`; zusätzlich Modellkennung, Vektordimension und Eingabelimit.
- **Index und Suche:** Vektorindex erstellen und ähnliche Vektoren als IDs und Scores liefern. Vorgesehen ist FAISS `IndexFlatIP` mit normalisierten Vektoren für Cosine Similarity.
- **Austauschbarkeit:** Zunächst eine konkrete Implementierung mit wiederverwendetem Modell und Index. Ein explizites Interface und die Auswahl alternativer Implementierungen folgen erst bei einer zweiten Variante. Bei gleichem Vertrag bleiben die Fachmodule unverändert; Tests können feste Vektoren liefern. Kein universelles KI-Framework oder Plugin-System.

Dokumentinhalte werden auf mehreren ermittelbaren Hierarchieebenen eingebettet, ohne lange Texte stillschweigend abzuschneiden. Query und Dokument verwenden kompatible Modell- und Verarbeitungseinstellungen. Ein Modellwechsel erfordert neue Embeddings und einen neuen Index. Startmodell, Behandlung langer Abschnitte und Zusammenführung verschiedener Trefferebenen sind noch offen.

Spätere KI-Funktionen stehen im [HLD](hld.md). Allgemeine Modellaufrufe gehören dann ebenfalls hierher; die anfragebezogene Passagenauswahl sowie Anweisungen und Prüfung von Zusammenfassungen gehören in die Fachmodule. Im MVP werden diese Erweiterungen nicht vorbereitet.

## Use Cases und interne Verarbeitung

| Benutzer-Use-Case aus dem HLD | Service-Operation (vorgeschlagen) | Interner Ablauf |
|---|---|---|
| UC 1: PDF zum Durchsuchen öffnen | `prepare_document(pdf_path) → DocumentInfo` | `pdf.py`: Elemente/Fundstellen ermitteln → `embeddings.py`: Texte aufbereiten und einbetten → `index.py`: Index mit Elementzuordnung aufbauen |
| UC 2: Informationen im PDF suchen | `search(document_id, query, limit) → list[SearchHit]` | `search.py`: Query einbetten → Vektorsuche → Treffer samt Originaltext und Fundstellen zusammenstellen |
| UC 3: Fundstelle im Original prüfen | `get_document(document_id) → Path` | Original-PDF bereitstellen; Navigation und Markierung anhand der bereits gelieferten Fundstellen übernimmt PDF.js im Frontend |

Ein `InfoRetriever`-Objekt in `service.py` hält Modelladapter, Dokumentelemente und Index für ein aktives PDF. Es verbindet die Schritte; die Verarbeitungsdetails bleiben in den Fachmodulen. Das Modell wird über mehrere Anfragen wiederverwendet. Erst eine vollständig erfolgreiche Aufbereitung stellt das Dokument als durchsuchbar bereit; kein Suchaufruf darf einen halbfertigen Index sehen. Fehler wie unlesbare PDFs, fehlender zugänglicher Text oder unbekannte Dokumente werden verständlich gemeldet.

## Datenmodelle und Originalbezug

`models.py` enthält Python-Darstellungen der fachlichen Daten, keine KI-Modelle:

- **Dokumentelement:** eindeutige ID, Originaltext, Hierarchieebene (Kapitel, Unterkapitel, Absatz, Satz) und gegebenenfalls übergeordnetes Element.
- **Fundstelle:** Seite und Positionsdaten; ein Element kann mehrere Rechtecke auf mehreren Seiten benötigen.
- **Suchtreffer:** Referenz auf das Dokumentelement, Suchscore und zugehörige Fundstellen.

**Indexeintrag → Dokumentelement → Originalfundstelle** bleibt eindeutig. Zusätzlich eingebetteter Kontext wie Überschriften ersetzt nicht den Originaltext. Wiederkehrende Texte und Regelnummern dürfen keine Zuordnung allein über Textgleichheit auslösen. Nicht zuverlässig erkennbare Hierarchie bleibt als Unsicherheit sichtbar.

### Dokumentstruktur: Befund und offene Lösungsidee

**Negativbefund:** Die getestete Docling-Konfiguration liefert für die Sportordnung keinen brauchbaren Kapitelbaum: Überschriften-Level sind teilweise falsch, die Elternreferenz der Überschriften ist durchgehend `#/body`. `DoclingDocument` kann die gewünschte Hierarchie darstellen, wird damit aber noch nicht zuverlässig befüllt. Auch Marker liefert falsche Überschriften und Level; die erprobte GPT-Korrektur verbessert Level, löst aber nicht die Auswahl geeigneter Gliederungsüberschriften.

**Experimentelle Lösungsidee:** Ein Chatmodell beurteilt Überschriftenkandidaten und liefert pro ID einen korrigierten Level oder „keine Gliederungsüberschrift“. Python übernimmt ausschließlich diese Strukturentscheidungen und baut passende Eltern-Kind-Beziehungen im `DoclingDocument` auf; Originaltext und Fundstellen bleiben unverändert. Die Beratung soll unabhängig von HTML oder Markdown sein.

**Noch nicht beschlossen:** Zu prüfen sind Zuverlässigkeit, Implementierungsaufwand, Laufzeit der lokalen Aufbereitung und Modellkorrektur sowie API-Kosten; Einrichtung und erster Start werden getrennt betrachtet. Ein Chatmodell zur Aufbereitung wäre eine Änderung der bisherigen MVP-Abgrenzung. Detailbefunde stehen in den Beobachtungen zu [Docling](../experiments/docling/observations.md) und [Marker](../experiments/marker/observations.md).

## Tests und Experimente

Es gelten [AGENTS.md](../AGENTS.md) und die dort eingeordneten [gemeinsamen Testregeln](../../nmt_lab/translator/how_to_test.md). Unit-Tests orientieren sich an den Fachmodulen und prüfen beobachtbares Verhalten; keine Pflichttests für private Hilfsfunktionen oder triviale Weiterleitungen. Integrationstests liegen unter `tests/integration`.

- Kleine PDFs prüfen Extraktion, Hierarchie und Fundstellen, insbesondere ähnlich formulierte Abschnitte mit unterschiedlichen Überschriften.
- Feste Vektoren prüfen die allgemeinen KI-Operationen und das Ranking; Fachtests prüfen zusätzlich die Zuordnung zu Dokumentelementen und Originalfundstellen. Integrationstests verwenden echtes FAISS und reale PDF-Verarbeitung. Service-Tests prüfen Abläufe und Zustandswechsel bei Erfolg und Fehlern.
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
