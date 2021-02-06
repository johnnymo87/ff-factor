# Base image
FROM python:3.9-buster AS base

ENV PYTHONPATH=.

COPY requirements.txt /tmp/requirements.txt
RUN  pip install --upgrade pip && \
  pip install pip-tools && \
  pip install -r /tmp/requirements.txt

# Release image
FROM base AS release

WORKDIR /app
COPY . /app

CMD python .
