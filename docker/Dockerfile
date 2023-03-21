FROM python:3-slim

ENV ARGS=''
WORKDIR /app

ARG CACHEBUST
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD python run.py ${ARGS}
