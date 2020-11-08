# Base image
FROM python:3.8.3-buster AS base

COPY requirements.txt /tmp/requirements.txt
RUN  pip3 install --upgrade pip && \
  pip3 install -r /tmp/requirements.txt

# Release image
FROM base AS release

WORKDIR /app
COPY . /app
ENV PYTHONPATH=.

RUN ln -sf /app/.python_history ~/.python_history

CMD python3 .
