# Minimalbasis: Python 3.9 in einer leichten Alpine-Variante
FROM python:3.9-alpine

# Arbeitsverzeichnis im Container
WORKDIR /app

# requirements.txt kopieren und Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren (app.py, templates/, usw.)
COPY . .

# Flask läuft standardmäßig auf Port 5000
EXPOSE 5000

# Starte Flask via Python
CMD ["python", "app.py"]
