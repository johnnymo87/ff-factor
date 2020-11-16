FROM postgres:13

ENV PYTHONPATH=.

COPY .bashrc /tmp/.bashrc
RUN cat /tmp/.bashrc >> /root/.bashrc

COPY requirements.txt /tmp/requirements.txt
RUN  pip3 install --upgrade pip && \
  pip3 install -r /tmp/requirements.txt

# Release image
FROM base AS release

WORKDIR /app
COPY . /app

CMD python3 .
