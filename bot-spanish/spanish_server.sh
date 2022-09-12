#!/bin/sh

cd /app/bot-spanish

time_to_sleep=660

while :
do
  echo "Sleeping for $time_to_sleep seconds"
  sleep $time_to_sleep
  echo "Slept for $time_to_sleep seconds"
  break
done

rasa run -m /app/bot-spanish/models --enable-api --cors "*" --debug -p 5008