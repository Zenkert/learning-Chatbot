FROM rasa/rasa:3.1.1

WORKDIR /app/bot-spanish

COPY . /app/bot-spanish

COPY /models /app/bot-spanish/models

COPY spanish_server.sh /app/bot-spanish

USER root

# RUN rasa train

RUN chmod +x /app/bot-spanish/spanish_server.sh

USER 1001

VOLUME /app/bot-spanish

VOLUME /app/bot-spanish/data

VOLUME /app/bot-spanish/models

EXPOSE 5008

ENTRYPOINT [ "/app/bot-spanish/spanish_server.sh" ]

# CMD [ "run", "-m", "/app/bot-spanish/models", "--enable-api", "--cors", "*", "--debug", "-p", "5008" ]

