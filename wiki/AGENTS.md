# Wiki Schema — KfW/Energieberater Domain

## 1. Zweck
Diese Datei steuert das Verhalten des LLM-Wiki-Compilers bei `openkb add`. Sie wird bei jedem Index-Durchlauf neu eingelesen. Änderungen sind sofort wirksam.

## 2. KfW-Förderprogramme-Mapping
Ordne alle erwähnten KfW-Programme folgenden Kategorien zu:
- **KfW 151** — Effizienzhaus (EH55, EH70, EH85, EH100, EH115)
- **KfW 152** — Einzelmaßnahmen (Fenster, Türen, Dämmung, Heizung)
- **KfW 153** — Heizungsförderung (Biomasse, Wärmepumpe, Solarthermie)
- **KfW 215** — Neubau EFH/ZFH (Effizienzhaus-Standard)
- **KfW 218** — Baubegleitung (Energieberater)
- **KfW 219** — Sanierung (Effizienzhaus, Einzelmaßnahmen)

Erstelle für jedes erwähnte Programm eine Concept-Seite unter `concepts/kfw-XXX.md` mit:
- Förderhöhe (Tilgungszuschuss in % oder Euro)
- Voraussetzungen (Antragsberechtigte, Mindestmaßnahmen)
- Kombinierbarkeit mit anderen Programmen
- Aktueller Stand (Stand: 2024/2025 — bei veralteten Angaben kennzeichnen)

## 3. Quellenpflicht (KRITISCH)
- **Förderbeträge, Zinssätze, Antragshöhen** müssen immer mit `doc_id` und Seitenangabe zitiert werden
- Format in Concept-Seiten: `[Quelle: doc_XXX, S. YY]`
- Ohne belegbare Quelle: keine Zahlenangabe, stattdessen "siehe offizielle KfW-Unterlagen"
- Bei Widersprüchen zwischen Quellen: beide angeben, keine eigene Auflösung

## 4. Fachbegriffe-Disambiguierung
Erstelle oder aktualisiere Concept-Seiten für folgende Begriffe:
- **U-Wert** — Wärmedurchgangskoeffizient (W/m²K), je nach Bauteil (Außenwand, Fenster, Dach)
- **Wärmedämmung** — Unterscheide: Außenwand, Dach, Kellerdecke, Bodenplatte
- **Lüftungsanlage** — kontrollierte Wohnraumlüftung (KWL), Feuchteschutz
- **Solarthermie** — Trinkwassererwärmung, Heizungsunterstützung
- **Effizienzhaus** — EH55 bis EH115, Referenzgebäude nach GEG
- **Energieausweis** — Bedarfsausweis (berechnet), Verbrauchsausweis (gemessen), Gültigkeit
- **GEG** — Gebäudeenergiegesetz (2020), ersetzt EnEV, Mindestanforderungen
- **EnEV** — veraltet seit 2020, nur noch für laufende Verfahren
- **Tilgungszuschuss** — nicht rückzahlbarer Anteil der KfW-Förderung
- **Referenzgebäude** — Vergleichsgebäude nach GEG für Effizienzhaus-Berechnung

## 5. Normative Referenzen
Wenn Dokumente folgende Normen erwähnen, verlinke auf die entsprechende Concept-Seite:
- **GEG** — Gebäudeenergiegesetz (aktuell gültig)
- **DIN 4108** — Wärmeschutz im Hochbau
- **DIN V 18599** — Energiebedarf von Gebäuden (Berechnungsverfahren)
- **DIN 1946-6** — Lüftung von Wohnungen

## 6. Umgang mit Widersprüchen
Wenn zwei oder mehr Dokumente widersprüchliche Angaben machen:
1. Beide Quellen mit `doc_id` und Seitenangabe nennen
2. Keine eigene Auflösung versuchen
3. Einen Warnhinweis ausgeben: "⚠️ Widerspruch zwischen Quellen — bitte prüfen"
4. Ggf. eine neue Concept-Seite "Widersprüche" anlegen

## 7. Allgemeine Verhaltensregeln
- Keine erfundenen Zahlen, Beträge oder Fristen
- Bei Unsicherheit: "Laut [Quelle] gilt … — bitte prüfen Sie die aktuellen Unterlagen"
- Aktualität: KfW-Programme ändern sich jährlich — kennzeichne veraltete Angaben
- Seitenstruktur: Jede Concept-Seite hat max. 300 Wörter, bei mehr Inhalt aufteilen

## 8. Quellverzeichnisstruktur
Erkenne die Kategorie eines Dokuments an seinem Pfad unter `raw/`:
- `raw/kfws/` → KfW-Förderprogramme, Merkblätter, Antragsunterlagen
- `raw/sanierung/` → Sanierungsratgeber, Dämmung, Fenster, Heizungstausch
- `raw/berechnungen/` → U-Wert-Tabellen, Energieausweis-Berechnung, GEG-Nachweise
- `raw/muster/` → Musterverträge, Antragsformulare, Checklisten

## 9. Standard-Wiki-Format (von OpenKB)
- sources/ — Document content. Short docs as .md, long docs as .json (per-page). Do not modify directly.
- sources/images/ — Extracted images from documents, referenced by sources.
- summaries/ — One per source document. Summary of key content.
- concepts/ — Cross-document topic synthesis. Created when a theme spans multiple documents.
- explorations/ — Saved query results, analyses, and comparisons worth keeping.
- reports/ — Lint health check reports. Auto-generated.
- index.md — Content catalog: every page with link, one-line summary, organized by category.
- log.md — Chronological append-only record of operations (ingests, queries, lints).
- Use [[wikilink]] to link other wiki pages.
- Standard Markdown heading hierarchy.
- Keep each page focused on a single topic.
- Do not include YAML frontmatter (---) in generated content.
