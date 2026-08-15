FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
        libegl1 \
        libgl1 \
        libxkbcommon0 \
        libdbus-1-3 \
        && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY app ./app

CMD ["smart-dash"]