FROM python:3-slim

ENV ARGS=''
WORKDIR /app

ARG CACHEBUST
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN rm -rf  /opt/conda/lib/python3.7/site-packages/nanome
COPY nanome  /opt/conda/lib/python3.7/site-packages/nanome

CMD python run.py ${ARGS}
