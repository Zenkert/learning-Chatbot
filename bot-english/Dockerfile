FROM rasa/rasa:3.1.1

WORKDIR /app/bot-english

COPY . /app/bot-english

COPY ./data /app/bot-english/data

# COPY config.yml /app/bot-english/

# COPY credentials.yml /app/bot-english/

USER root

RUN rasa train

USER 1001

VOLUME /app/bot-english

VOLUME /app/bot-english/data

VOLUME /app/bot-english/models

EXPOSE 5005

CMD [ "run", "-m", "/app/bot-english/models", "--enable-api", "--cors", "*", "--debug", "-p", "5005" ]

