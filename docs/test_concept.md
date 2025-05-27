# Testkonzept

## Überblick

1. **Unit-Tests** schnell und gezielt sind → perfekt für Feedback während Entwicklung
2. **Integrationstests** uns absichern, dass Module zusammenspielen → perfekt für reale Szenarien
3. **Systemtests** das große Ganze abdecken → perfekt, um echte Nutzersicht zu prüfen

Aktuell gibt es **45 Unit-Tests** und **21 Integrationstests**. Die Tests werden mit Hilfe des Tools `pytest` durchgeführt. Dazu wird der Befehl

`python3 -m pytest --cov=application --cov=domain --cov=infrastructure --cov-report=html  tests`

Vor jedem Release ausgeführt. Damit ein Release erfolgen kann, muss die Gesamt-Coverage bei über 80% liegen. 
Absolut abdeckendes Testing ist nicht zielführend, da der Aufwand mit steigender Coverage exponentiell steigt,
was zu vielen redundanten Tests und stark erhöhtem Aufwand führt. Zudem wird darauf geachtet, 
dass alle relevanten Code-Dateien eine eigenständige Coverage von über 80% aufweisen. Dabei gibt es Ausnahmen,
wie beispielsweise Source-Code, in denen lediglich Interfaces oder Konstanten deklariert sind.

Jeder Release enthält einen vollständigen Report der durchgeführten Unit-, Integrations- und Systemtests.

---

## Unit-Tests

Unit-Tests prüfen **einzelne, deterministische Komponenten isoliert**.  
Sie dienen der Prüfung einer Komponente oder eines Moduls, ohne dass externe Abhängigkeiten (wie z.B. Datensätze oder Netzwerke) angesprochen werden.

Wir verwenden hier **Mocks/Stubs** für alles, was nicht rein lokal und vorhersagbar ist.  
Beispiele:
- Logikmodule
- Datenparser
- Validierungsfunktionen

---

## Integrationstests

Integrationstests prüfen **das Zusammenspiel mehrerer Komponenten**, vor allem, wenn:
- externe oder nondeterministische Abhängigkeiten dabei sind (z. B. AI-Aufrufe, externe Services, Datenbanken)
- Module miteinander reden müssen (und nicht nur isoliert laufen)

Beispiele:
- Serviceklassen, die AI-Modelle aufrufen und Ergebnisse weiterreichen
- Komponenten, die mit der Datenbank interagieren

---

## Systemtests

Systemtests prüfen die **ganze Anwendung als End-to-End-System**, inklusive:
- Benutzeroberfläche (UI)
- Backend
- Datenbank
- externe Services

Hier wird die Anwendung so getestet, wie es ein echter Benutzer erleben würde. Somit wird sichergestellt, dass der Verbund aller Komponenten funktioniert.

---