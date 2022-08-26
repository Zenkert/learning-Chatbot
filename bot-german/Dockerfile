FROM rasa/rasa:3.1.1

WORKDIR /app/bot-german

COPY . /app/bot-german

COPY wait-for-it.sh /app/bot-german

COPY german_server.sh /app/bot-german

USER root

RUN rasa train

RUN chmod +x /app/bot-german/german_server.sh

USER 1001

VOLUME /app/bot-german

VOLUME /app/bot-german/data

VOLUME /app/bot-german/models

EXPOSE 5006

ENTRYPOINT [ "/app/bot-german/german_server.sh" ]

# CMD [ "run", "-m", "/app/bot-german/models", "--enable-api", "--cors", "*", "--debug", "-p", "5006" ]

