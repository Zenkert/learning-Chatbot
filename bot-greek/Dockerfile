FROM rasa/rasa:3.1.1

WORKDIR /app/bot-greek

COPY . /app/bot-greek

COPY /models /app/bot-greek/models

COPY greek_server.sh /app/bot-greek

USER root

# RUN rasa train

RUN chmod +x /app/bot-greek/greek_server.sh

USER 1001

VOLUME /app/bot-greek

VOLUME /app/bot-greek/data

VOLUME /app/bot-greek/models

EXPOSE 5007

ENTRYPOINT [ "/app/bot-greek/greek_server.sh" ]

# CMD [ "run", "-m", "/app/bot-greek/models", "--enable-api", "--cors", "*", "--debug", "-p", "5007" ]

