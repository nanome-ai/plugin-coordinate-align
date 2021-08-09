FROM nanome/plugin-env

ENV ARGS=''
WORKDIR /app

ARG CACHEBUST
COPY ../requirements.txt .
RUN pip install -r requirements.txt

COPY plugin_align_tool/ .

CMD python run.py ${ARGS}
