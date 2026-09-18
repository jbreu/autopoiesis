# Autopoiesis

Ein Git-Repo, das seine Entwicklungsumgebung und einen Coding-Agenten mitbringt.
OpenHands Agent Canvas läuft im Container und ist über den Browser erreichbar.
Der Agent arbeitet am gemounteten Checkout, führt Tests aus und kann Änderungen
als Commits und GitHub-Pull-Requests abliefern.

Als überschaubares Beispiel enthält das Repo eine Python-CLI für Textstatistiken.
Sie hat keine Laufzeitabhängigkeiten. Die Anwendung lässt sich durch ein eigenes
Projekt ersetzen; Container, Arbeitsregeln und CI werden entsprechend angepasst.

## Voraussetzungen

- Git, Docker Engine/Desktop mit Compose v2 und Python 3.11 oder neuer für die
  einmalige lokale Konfiguration. Unter Windows die Befehle in WSL2 ausführen.
- Ein für OpenHands geeigneter Modellzugang. Provider, Modell und API-Key werden
  beim ersten Start in der Oberfläche eingerichtet. Modellaufrufe können Kosten
  verursachen; dieses Repo enthält weder Modellgewichte noch einen Modellzugang.
- Für GitHub-Push und PRs: ein auf dieses Repo begrenzter Token mit Contents: write
  und Pull requests: write. Für lokale Änderungen wird kein GitHub-Token benötigt.

## Start

Repository klonen und starten:

```bash
git clone https://github.com/jbreu/autopoiesis.git
cd autopoiesis
python3 scripts/init_env.py
docker compose up -d --build --wait --wait-timeout 180
```

Dann [Agent Canvas](http://localhost:8000/canvas) öffnen. Im Einrichtungsdialog den
lokalen Backend-Server, einen Coding-Agenten und den Modellzugang konfigurieren.
Der Projektpfad **im Container ist `/projects/app`**. Falls nach einem Backend-Key
gefragt wird, den lokal erzeugten Wert LOCAL_BACKEND_API_KEY aus .env verwenden.
Beim ersten Auftrag ausdrücklich darum bitten, AGENTS.md zu lesen.

`scripts/init_env.py` erstellt .env mit zufälligen Schlüsseln und passenden
Benutzer-IDs auf Linux. Eine bestehende Datei bleibt unverändert. Bei einem
root-eigenen Linux-Checkout einen normalen Benutzer als Eigentümer verwenden;
der Container läuft als unprivilegierter Benutzer openhands.

## GitHub aktivieren

1. In der ignorierten .env den Wert GH_TOKEN ergänzen. Den Token lokal eintragen,
   nicht in einen Agentenprompt, Commit oder Chat kopieren.
2. AGENT_GIT_NAME und AGENT_GIT_EMAIL bei Bedarf anpassen.
3. Für origin eine HTTPS-URL ohne eingebetteten Token verwenden:
   `git remote set-url origin https://github.com/jbreu/autopoiesis.git`.
4. `docker compose up -d --force-recreate` ausführen.
5. Mit `docker compose exec agent gh auth status` und
   `docker compose exec agent git remote -v` den Zugang prüfen.

Der Entrypoint richtet Git-Identität und den GitHub-Credential-Helper ein. Der
Agent kann danach mit git committen/pushen und mit gh einen PR erstellen. Als
Arbeitsregel gilt ein neuer ai/*-Branch pro Auftrag und ein Draft-PR als Ergebnis.
Branch-Schutz für main wird separat auf GitHub eingerichtet; AGENTS.md ist eine
Arbeitsanleitung und erzwingt keine GitHub-Berechtigungen.

## Erster Agentenauftrag

Ein vollständiger Beispielauftrag steht in [docs/first-task.md](docs/first-task.md):
Die CLI soll eine JSON-Ausgabe erhalten, einschließlich Tests und Draft-PR.
Das Feature ist bewusst noch nicht implementiert und dient als erster echter
Entwicklungsauftrag. Weboberfläche und Terminal teilen denselben Checkout;
zunächst immer nur einen schreibenden Auftrag gleichzeitig ausführen.

## Tests und Beispielanwendung

Im laufenden Container:

```bash
docker compose exec agent sh scripts/check.sh
docker compose exec -e PYTHONPATH=src agent python3 -m repo_demo "hello world"
```

Lokal ohne Container:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
PROJECT_PYTHON=.venv/bin/python sh scripts/check.sh
PYTHONPATH=src .venv/bin/python -m repo_demo "hello world"
```

Die Ausgabe enthält Characters, Words und Lines. Zeichen werden als Unicode-Code-
Points gezählt; Wörter sind durch Whitespace getrennt. Eine abschließende Newline
erzeugt keine zusätzliche Leerzeile. Ohne Textargument liest die CLI stdin.

## Betrieb

- Status: `docker compose ps`
- Logs: `docker compose logs -f --tail=100 agent`
- Shell: `docker compose exec agent bash`
- Stoppen: `docker compose down`
- Nach Änderungen am Image: `docker compose up -d --build`
- Einen aktiven Auftrag über die Oberfläche stoppen; zum Beenden aller Prozesse
  `docker compose stop agent` verwenden.

Sitzungen, Einstellungen und Modellzugänge liegen im benannten Volume agent-state.
`docker compose down` erhält dieses Volume. `docker compose down --volumes` löscht
den Zustand und sollte nur für einen gewollten Reset verwendet werden. Den Wert
OH_SECRET_KEY zusammen mit dem Volume aufbewahren; nicht beliebig neu generieren.

Die Oberfläche ist standardmäßig nur über localhost erreichbar. Für einen
Server zunächst einen SSH-Tunnel verwenden, beispielsweise
`ssh -L 8000:127.0.0.1:8000 user@server`. Der Container mountet ausschließlich
diesen Checkout und sein Zustandsvolume. Ein Host-Docker-Socket wird nicht
eingebunden; Docker-Builds laufen in der CI oder auf dem Host.

## CI und Entwicklungsumgebung

GitHub Actions führt dieselben Prüfungen über scripts/check.sh aus, baut das
Python-Paket und startet zusätzlich das Agenten-Image. Der Container-Test prüft
Weboberfläche, Toolchain und Schreibzugriff. Er verwendet weder echte Modell-Keys
noch GitHub-Schreibrechte und testet deshalb keine LLM-Inferenz oder PR-Erstellung.

Mit VS Code / Dev Containers kann die vorhandene Compose-Umgebung geöffnet werden.
Vorher scripts/init_env.py ausführen. Ein Container-Neustart stellt vorhandene
Sessions bereit; eine automatische Fortsetzung unterbrochener Aufgaben ist kein
Versprechen dieses PoC.

## Aufbau und nächste Schritte

Siehe [docs/architecture.md](docs/architecture.md) für Zuständigkeiten und Grenzen.
Chat-Adapter, Aufgabenwarteschlange und automatische Auswahl neuer Arbeit sind
mögliche Ausbaustufen. Der PoC wird zunächst über explizite Browser-Aufträge gesteuert.

Upstream: [OpenHands](https://github.com/OpenHands/OpenHands),
[Docker-Betrieb](https://docs.openhands.dev/openhands/usage/agent-canvas/backend-setup/docker),
[Ersteinrichtung](https://docs.openhands.dev/openhands/usage/agent-canvas/first-time-setup).
Der Harness ist auf Agent Canvas 1.20.0 festgelegt. Systempakete stammen beim
Build aus der Paketquelle des Basisimages; für bytegenau reproduzierbare Builds
wären zusätzlich Image-Digests und Paket-Snapshots erforderlich.
