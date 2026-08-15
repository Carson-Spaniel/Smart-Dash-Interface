FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
        # OpenGL / EGL
        libegl1 \
        libgl1 \
        \
        # GLib / fonts / DBus
        libglib2.0-0 \
        libfontconfig1 \
        libdbus-1-3 \
        \
        # Keyboard / input
        libxkbcommon0 \
        libxkbcommon-x11-0 \
        \
        # Kerberos / GSSAPI
        libkrb5-3 \
        libgssapi-krb5-2 \
        \
        # X11
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        \
        # XCB dependencies used by Qt
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-shape0 \
        libxcb-shm0 \
        libxcb-sync1 \
        libxcb-xfixes0 \
        libxcb-xkb1 \
        \
        # XCB rendering / utilities
        libxcb-render0 \
        libxcb-util1 \
        \
        # X11 extensions
        libxext6 \
        libxrender1 \
        libxi6 \
        libxfixes3 \
        libxrandr2 \
        libxdamage1 \
        libxcomposite1 \
        libxcursor1 \
        libxinerama1 \
        libxtst6 \
        \
        # Font / text rendering
        libfreetype6 \
        \
        # Misc Qt runtime dependencies
        libpcre2-16-0 \
        libdouble-conversion3 \
        libzstd1 \
        && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY app ./app

RUN pip install --no-cache-dir .

CMD ["smart-dash"]