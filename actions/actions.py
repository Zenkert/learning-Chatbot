from random import choices
from urllib import response
from matplotlib.pyplot import text
import pandas as pd
from typing import Any, Text, Dict, List
import json
import actions

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from actions import main


class ActionSubmit(Action):

    def name(self) -> Text:
        return "action_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        tracker_events = tracker.events

        transcript = []

        for data in tracker_events:
            m = 1
            if data['event'] == 'user':
                try:
                    user_uttered = data['text']
                    user_uttered_formatted = f'User: {user_uttered}'
                    transcript.append(user_uttered_formatted)
                except KeyError:
                    pass

            elif data['event'] == 'bot':
                try:
                    bot_uttered = data['text']
                    user_uttered_formatted = f'Bot: {bot_uttered}'
                    transcript.append(user_uttered_formatted)
                except KeyError:
                    pass

        dj = pd.DataFrame(transcript, columns=['Transcript'])
        dj.to_excel('user_transcript.xlsx')

        return []


class ActionUserData(Action):

    def name(self) -> Text:
        return "action_save_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # replacing {'key': 'value'} to {"key": "value"} to get valid json
        msg = tracker.latest_message['text'].replace("'", "\"")
        print(msg)
        # converting string to json using loads
        try:
            message = json.loads(msg)
            print(message)
            name: str = message['name']
            id: int = message['id']
            language: str = message['language']

            dispatcher.utter_message(response="utter_name")
            return [SlotSet("name", name), SlotSet("id", id), SlotSet("language", language)]
        except:
            print("This is an error!")

        dispatcher.utter_message(text=f"Hey, how are you doing today?")
        return []


class ActionTellSubjects(Action):

    def name(self) -> Text:
        return "action_tell_subjects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subs = main.get_subjects(collection_name='subjects')

        try:
            subject = next(tracker.get_latest_entity_values(
                entity_type="subject"))
        except:
            subject = None

        if subject is not None:
            dispatcher.utter_message(
                text=f"I will query my database about {subject}")
            print("Subject: ", subject)

        else:
            dispatcher.utter_message(
                text=f"These are the some of the subjects available: {subs}")
            print("No entity: ", subject)

        # return [SlotSet("id", id), SlotSet("name", name), SlotSet("language", language)]
        return []


class ActionGiveSuggestion(Action):

    def name(self) -> Text:
        return "action_give_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subs = main.get_subjects(collection_name='subjects')
        dispatcher.utter_message(
            text=f"These are some of the subjects I'd suggest: {subs}")

        return []
