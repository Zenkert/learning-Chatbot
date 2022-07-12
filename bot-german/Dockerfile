FROM rasa/rasa:3.1.1

WORKDIR /app

COPY . /app

USER root

RUN rasa train

USER 1001

VOLUME /app

VOLUME /app/data

VOLUME /app/models

CMD [ "run", "-m", "/app/models", "--enable-api", "--cors", "*", "--debug", "-p", "8000" ]

