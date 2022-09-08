#!/bin/sh

cd /app/bot-greek

while :
do
  sleep 420
  echo "Waited for 420 seconds"
  break
done

rasa run -m /app/bot-greek/models --enable-api --cors "*" --debug -p 5007