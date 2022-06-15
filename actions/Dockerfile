FROM rasa/rasa-sdk:3.1.1

WORKDIR /app

COPY requirements.txt requirements.txt

USER root

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

EXPOSE 5055

USER 1001

