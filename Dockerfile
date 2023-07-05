
FROM python:3
COPY requirements.txt ./

# # Setzen Sie das Arbeitsverzeichnis auf /app
# WORKDIR /app
# # Kopieren Sie die Projektdateien in das Arbeitsverzeichnis
# COPY . /app

# Erstellen Sie eine virtuelle Umgebung und aktivieren Sie sie
RUN python -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

## https://docs.docker.com/build/install-buildx/
# syntax=docker/dockerfile:1
FROM docker:23.0.1
COPY --from=docker/buildx-bin:latest /buildx /usr/libexec/docker/cli-plugins/docker-buildx
RUN docker buildx version
RUN docker buildx install

FROM returntocorp/semgrep:latest
FROM alpine/flake8:6.0.0
ENV CI_COMMIT_SHORT_SHA=${CI_COMMIT_SHORT_SHA}
ENV CI_PIPELINE_IID=${CI_PIPELINE_IID}
ENV WIKI_PERSONAL_TOKEN=${WIKI_PERSONAL_TOKEN}
ENV JIRA_PERSONAL_TOKEN=${JIRA_PERSONAL_TOKEN}
ENV JIRA_LOGIN_URL=${JIRA_LOGIN_URL}

# Führen Sie das Hauptskript aus, wenn der Container gestartet wird
CMD ["python3", "main.py"]
# CMD ["python", "main.py"]

# starting CR sync
RUN python