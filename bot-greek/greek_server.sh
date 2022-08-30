#!/bin/sh

cd /app/bot-greek

while :
do
  sleep 480
  echo "Waited for 480 seconds"
  break
done

rasa run -m /app/bot-greek/models --enable-api --cors "*" --debug -p 5007