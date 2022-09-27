FROM rasa/rasa:3.1.1

WORKDIR /app/bot-english

COPY . /app/bot-english

COPY ./models /app/bot-english/models

# COPY english_server.sh /app/bot-english

USER root

# RUN rasa train

# RUN chmod +x /app/bot-english/english_server.sh

USER 1001

VOLUME /app/bot-english

VOLUME /app/bot-english/data

VOLUME /app/bot-english/models

EXPOSE 5005

# ENTRYPOINT [ "/app/bot-english/english_server.sh" 

CMD [ "run", "-m", "/app/bot-english/models", "--enable-api", "--cors", "*", "--debug", "-p", "5005" ]

