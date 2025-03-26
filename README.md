# Darts-Webanwendung (501 Punkte)  
Diese Webanwendung ermöglicht es, das klassische Darts-Spiel **501 (mit optionalem Double-Out)** allein oder zu zweit über eine intuitive Weboberfläche zu spielen. Die Anwendung wurde mit **Python Flask** und **MySQL** entwickelt und per **Docker Compose** containerisiert.

---

## Funktionen

- Registrierung mit **Benutzername**, **Passwort** und **E-Mail-Adresse**
- Login & Logout
- Spielstart für **1 oder 2 Spieler**
- Option **Double-Out aktivieren**
- Eingabe von Würfen via Buttons (1–20 mit Single/Double/Triple, 25, 50, Miss)
- **Bust-Regel** und Double-Out-Regel werden korrekt umgesetzt
- Anzeige von Punktestand, aktueller Spieler und **Wurfanzahl**
- REST-API-Endpunkt: `/api/scores` zur Abfrage des Spielstands als JSON
- Bereitstellung als **Docker Compose Setup** (App + MySQL)

---

## Installation & Start

### Voraussetzungen
- Docker  
- Docker Compose

### Setup starten

### bash
git clone https://github.com/matthieu308/my_dart_app.git
cd my_dart_app
docker compose up --build

