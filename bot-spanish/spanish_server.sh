#!/bin/sh

cd /app/bot-spanish

while :
do
  sleep 700
  echo "Waited for 700 seconds"
  break
done

rasa run -m /app/bot-spanish/models --enable-api --cors "*" --debug -p 5008