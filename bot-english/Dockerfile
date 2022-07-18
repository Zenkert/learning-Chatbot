FROM rasa/rasa:3.1.1

WORKDIR /app/bot-english

COPY . /app/bot-english

USER root

RUN rasa train

USER 1001

VOLUME /app/bot-english

VOLUME /app/bot-english/data

VOLUME /app/bot-english/models

CMD [ "run", "-m", "/app/bot-english/models", "--enable-api", "--cors", "*", "--debug" ]

