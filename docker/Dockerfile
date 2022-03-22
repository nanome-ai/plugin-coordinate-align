FROM python:3-slim

ENV ARGS=''
WORKDIR /app

ARG CACHEBUST
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY run.py .
ADD plugin_coordinate_align plugin_coordinate_align

CMD python run.py ${ARGS}
