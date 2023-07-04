# syntax = docker/dockerfile:1.2
FROM python:3.11.3-alpine3.18

WORKDIR /opt/hubstaff

COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache pip3 install -U -r requirements.txt

COPY *.py settings.yaml ./

ENTRYPOINT ["python3", "hubstaff_app.py"]
