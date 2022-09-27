#!/bin/sh

cd /app/bot-german

time_to_sleep=180

while :
do
  echo "Sleeping for $time_to_sleep seconds"
  sleep $time_to_sleep
  echo "Slept for $time_to_sleep seconds"
  break
done

rasa run -m /app/bot-german/models --enable-api --cors "*" --debug -p 5006