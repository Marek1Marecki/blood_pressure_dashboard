FROM python:3.12-slim

# Zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Katalog roboczy
WORKDIR /app

# Systemowe zależności (plotly, pillow itp.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalacja zależności Pythona
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod
COPY . .

# Port Dash (domyślnie)
EXPOSE 8050

# Start aplikacji
CMD ["python", "app.py"]
