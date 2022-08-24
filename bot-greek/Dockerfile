FROM rasa/rasa:3.1.1

WORKDIR /app/bot-greek

COPY . /app/bot-greek

USER root

RUN rasa train

USER 1001

VOLUME /app/bot-greek

VOLUME /app/bot-greek/data

VOLUME /app/bot-greek/models

EXPOSE 5007

CMD [ "run", "-m", "/app/bot-greek/models", "--enable-api", "--cors", "*", "--debug", "-p", "5007" ]

