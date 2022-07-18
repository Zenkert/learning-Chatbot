FROM rasa/rasa:3.1.1

WORKDIR /app/bot-german

COPY . /app/bot-german

USER root

RUN rasa train

USER 1001

VOLUME /app/bot-german

VOLUME /app/bot-german/data

VOLUME /app/bot-german/models

CMD [ "run", "-m", "/app/bot-german/models", "--enable-api", "--cors", "*", "--debug", "-p", "8000" ]

