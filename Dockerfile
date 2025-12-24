# ===============================
# STAGE 1: build dependencies
# ===============================
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ===============================
# STAGE 2: runtime
# ===============================
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8050

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8050/health || exit 1

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8050", "app:server"]
