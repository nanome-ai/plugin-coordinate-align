FROM python:3

ENV ARGS=''
WORKDIR /app

ARG CACHEBUST
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY run.py .
ADD plugin_align_tool plugin_align_tool

CMD python run.py ${ARGS}
