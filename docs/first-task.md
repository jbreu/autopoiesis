# Erster Entwicklungsauftrag

Diesen Auftrag nach Einrichtung von Modell- und GitHub-Zugang in der
Weboberfläche verwenden. Das Projektverzeichnis ist /projects/app.

> Lies AGENTS.md und README.md. Erweitere die Beispiel-CLI um eine Option --json.
> Sie soll ein JSON-Objekt mit den Integer-Feldern characters, words und lines
> ausgeben. Ohne --json soll die bestehende Textausgabe unverändert bleiben.
> Die Option muss sowohl mit einem Textargument als auch mit stdin funktionieren.
> Ergänze Verhaltenstests, auch für leeren Text und Unicode-Eingaben, und führe
> sh scripts/check.sh aus. Arbeite auf einem neuen ai/json-output-Branch,
> committe die Änderung, pushe den Branch und öffne einen Draft-PR gegen main.
> Beschreibe im PR die Änderung und die ausgeführten Prüfungen. Stoppe danach.

## Akzeptanzkriterien

- JSON wird mit einem echten Parser überprüft und enthält genau die drei Felder.
- Bestehende CLI-Tests bleiben erfolgreich.
- Der PR enthält die Implementierung und die relevanten Tests.
- GitHub Actions ist erfolgreich; die lokale Agentenantwort allein gilt nicht
  als unabhängiger CI-Nachweis.
