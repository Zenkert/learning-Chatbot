FROM rasa/rasa:3.1.1

WORKDIR /app/bot-spanish

COPY . /app/bot-spanish

USER root

RUN rasa train

USER 1001

VOLUME /app/bot-spanish

VOLUME /app/bot-spanish/data

VOLUME /app/bot-spanish/models

EXPOSE 5008

CMD [ "run", "-m", "/app/bot-spanish/models", "--enable-api", "--cors", "*", "--debug", "-p", "5008" ]

