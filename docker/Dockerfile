FROM nanome/plugin-env

ENV ARGS=''
WORKDIR /app

ARG CACHEBUST
COPY ../requirements.txt .
RUN pip install -r requirements.txt

COPY align_plugin/ .

CMD python run.py ${ARGS}
