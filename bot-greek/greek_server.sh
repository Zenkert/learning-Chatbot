#!/bin/sh

cd /app/bot-greek

time_to_sleep=420

while :
do
  echo "Sleeping for $time_to_sleep seconds"
  sleep $time_to_sleep
  echo "Slept for $time_to_sleep seconds"
  break
done

rasa run -m /app/bot-greek/models --enable-api --cors "*" --debug -p 5007