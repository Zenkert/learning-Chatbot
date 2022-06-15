from re import sub
import pandas as pd
from typing import Any, Text, Dict, List
import json

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions import main
from fuzzywuzzy import process


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
        print('msg: ', msg)
        # converting string to json using loads
        try:
            message = json.loads(msg)
            print('message: ', message)
            name: str = message['name']
            id: int = message['id']
            language: str = message['lang']
            print('name: ', name, id, language)
            dispatcher.utter_message(text=f'Hey {name}, how are you doing?')
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
        name = tracker.get_slot('name')
        print('name: ', name)

        subs = main.get_subjects(collection_name='subjects')

        user_input = tracker.latest_message.get('text')

        fnd, common_value = process.extractOne(user_input, subs)
        print("fnd: ", fnd, 'common value: ', common_value)

        buttons = [{'title': 'Yes', 'payload': '/user_affirm{"subj":"'+fnd+'"}'},  # add subject as entity
                   {'title': 'No', 'payload': '/user_deny'}]

        if fnd is not None:

            if common_value >= 70:
                dispatcher.utter_message(
                    text=f"I found {fnd!r} in my database. Is that what you mean?", buttons=buttons)
                return []

            elif 50 <= common_value < 70:
                dispatcher.utter_message(
                    text=f"I think this is the one: {fnd}. Is this what you mean?", buttons=buttons)
                return []

        try:
            subject = next(tracker.get_latest_entity_values(
                entity_type="subject"))
        except:
            subject = None

        if subject is not None:
            dispatcher.utter_message(
                text=f"I will query my database about {subject}")
            print("Subject: ", subject)
            print(f"I will query my database about {subject}")

        else:
            buttons = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                       for sub in subs]

            dispatcher.utter_message(
                text=f"I couldn't find anything related to that subject. These are some of the subjects available.", buttons=buttons)

        return []


class ActionGiveSuggestion(Action):

    def name(self) -> Text:
        return "action_give_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subs = main.get_subjects(collection_name='subjects')

        buttons = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                   for sub in subs]

        dispatcher.utter_message(
            text="These are some of the subjects I'd suggest: ", buttons=buttons)

        return []


class ActionTellTopics(Action):

    def name(self) -> Text:
        return "action_tell_topics"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subject = tracker.get_slot('subj')
        print('subj -> action_tell_topics: ', subject)

        topics_available = main.get_topics(subject)

        buttons = [{"title": topic, "payload": '/inform_new{"topic":"'+topic+'"}'}
                   for topic in topics_available]

        dispatcher.utter_message(
            text=f'Please select a topic: {topics_available}', buttons=buttons)

        return []
