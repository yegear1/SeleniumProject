FROM python:3.11-slim

ARG CHROME_VERSION="137.0.7151.103-1"

ENV TZ=America/Sao_Paulo

ENV VENV_PATH=/opt/venv
ENV PATH="$VENV_PATH/bin:$PATH"
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata wget gnupg2 ca-certificates \
    fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libasound2 libdbus-1-3 libxtst6 libxss1 libdrm2 libgbm1 \
    gpg \
    && \
    wget -qO - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable=${CHROME_VERSION} && \
    rm -rf /var/lib/apt/lists/*
    
RUN useradd -ms /bin/bash appuser

RUN python3 -m venv $VENV_PATH && \
    chown -R appuser:appuser $VENV_PATH
    
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser main.py scrapers.py utils.py ./

RUN chown -R appuser:appuser /app

USER appuser

CMD ["python3", "main.py"]