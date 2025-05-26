# Testkonzept

## Überblick

1. **Unit-Tests**  
2. **Integrationstests**  
3. **Systemtests**

Aktuell gibt es **32 Unit-Tests** und **19 Integrationstests**.

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

## Warum diese Aufteilung?

Wir splitten die Tests auf, weil:
- **Unit-Tests** schnell und gezielt sind → perfekt für Feedback während Entwicklung
- **Integrationstests** uns absichern, dass Module zusammenspielen → perfekt für reale Szenarien
- **Systemtests** das große Ganze abdecken → perfekt, um echte Nutzersicht zu prüfen

Wenn wir alles in einer Schicht testen würden, wäre es entweder:
- zu langsam und fragil (nur Systemtests), oder
- zu kurzsichtig und unvollständig (nur Unit-Tests).

Durch die Aufteilung bleiben die Tests **effizient, stabil und aussagekräftig**.

---
