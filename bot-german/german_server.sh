#!/bin/sh

cd /app/bot-german

while :
do
  sleep 180
  echo "Waited for 180 seconds"
  break
done

rasa run -m /app/bot-german/models --enable-api --cors "*" --debug -p 5006