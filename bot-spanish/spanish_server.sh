#!/bin/sh

cd /app/bot-spanish

while :
do
  sleep 660
  echo "Waited for 660 seconds"
  break
done

rasa run -m /app/bot-spanish/models --enable-api --cors "*" --debug -p 5008