# Architektur

## Ablauf

1. Der Benutzer erteilt einen Auftrag in Agent Canvas.
2. Die Harness liest das Projekt in /projects/app und spricht mit dem ausgewählten
   Modellanbieter. Dateizugriffe, Codeausführung und Git-Kommandos erfolgen im Container.
3. Der Agent entwickelt auf einem ai/*-Branch und prüft mit scripts/check.sh.
4. Mit konfiguriertem GH_TOKEN kann er den Branch pushen und einen Draft-PR erstellen.
5. GitHub Actions prüft Code und Container; der Benutzer entscheidet über den Merge.

## Zuständigkeiten

| Bestandteil | Verantwortlich für |
| --- | --- |
| src/repo_demo und tests | Beispielanwendung und Verhaltenstests |
| Dockerfile.agent | OpenHands-Basisimage, Python-Tools und GitHub CLI |
| compose.yaml | Lokalen Start, Workspace, Ressourcen und persistente Daten |
| AGENTS.md | Projektwissen und vereinbarten Arbeitsablauf |
| scripts/check.sh | Gemeinsame Prüfungen für Mensch, Agent und CI |
| .github/workflows/ci.yml | Unabhängige Prüfungen im CI-Runner |
| .devcontainer/devcontainer.json | Optionalen interaktiven IDE-Zugang |

## Warum die Projekt-Tools isoliert installiert werden

OpenHands bringt eine eigene Python-Umgebung mit. Das Beispiel installiert seine
Entwicklungswerkzeuge in /opt/poc-tools und verwendet PROJECT_PYTHON explizit.
Der PATH der Harness bleibt erhalten, damit deren Entrypoint weiterhin die
ursprünglichen Pakete findet. Der eigene Entrypoint ergänzt die Git-Konfiguration
und startet anschließend den offiziellen OpenHands-Entrypoint.

## Zustand und Grenzen

Der komplette Checkout einschließlich .git wird schreibbar eingebunden. Ein Commit
überlebt somit einen Container-Neustart auch ohne Push. .env ist lokal und ignoriert;
Container-Umgebung und gemountete Dateien sind für den Agenten grundsätzlich lesbar.
Ein separater, nur für dieses Repo berechtigter Token begrenzt dessen GitHub-Zugang.
Die Containerisierung ist keine Isolation gegenüber einem vom Agenten lesbaren Secret.

Das Volume enthält Sitzungen, Einstellungen und Modellzugänge. Es gehört nicht zur
Git-Historie. Für einen neuen Rechner werden Repo, Laufzeitkonfiguration und bei
gewünschter Session-Kontinuität ein Backup des Volumes benötigt.

Die Healthcheck prüft HTTP und Content-Type der Weboberfläche sowie /ready des
Backends. Ein tatsächlicher Modellauftrag und ein GitHub-Push benötigen eigene
Zugangsdaten und sind als manueller
End-to-End-Test vorgesehen. Die maximale Reparaturzahl in AGENTS.md ist eine Anweisung;
ein technisch erzwungenes Auftragszeitlimit benötigt einen externen Dispatcher.

## Ausbau

- Chat: authentifizierter Adapter ordnet einen Chat einer Agentensitzung zu.
- Warteschlange: speichert Auftrag, Ausgangscommit, Branch, Session-ID und Status.
- Parallelität: eigener Clone oder Worktree je Auftrag; keine gemeinsam
  beschriebene Arbeitskopie.
- Automatisierung: explizite Issues/Labels oder CI-Ereignisse als Aufgabenquelle;
  maximale Laufzeit und Budget außerhalb des veränderbaren Checkouts kontrollieren.
- GitLab: Git-Zugriff und PR-Helfer durch passende GitLab-Konfiguration ersetzen.
