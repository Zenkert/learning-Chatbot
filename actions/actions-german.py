import pandas as pd
from typing import Any, Text, Dict, List
import json

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions import main
from fuzzywuzzy import process


class ActionTellSubjectsGerman(Action):

    def name(self) -> Text:
        return "action_tell_subjects_german"

    @staticmethod
    def user_language():
        pass

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subs = main.get_subjects(collection_name='subjects')

        user_input = tracker.latest_message.get('text')

        fnd, common_value = process.extractOne(user_input, subs)
        print("fnd: ", fnd, 'common value: ', common_value)

        buttons = [{"title": sub, "payload": '/inform_new_german{"subj":"'+sub+'"}'}
                   for sub in subs]

        dispatcher.utter_message(
            text=f"Dies sind nur einige der verfügbaren Themen.", buttons=buttons)

        return []


class ActionTellTopicsGerman(Action):

    def name(self) -> Text:
        return "action_tell_topics_german"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subject = tracker.get_slot('subj')
        print('subj -> action_tell_topics: ', subject)

        topics_available = main.get_topics(subject)

        buttons = [{"title": topic, "payload": '/inform_new_german{"topic":"'+topic+'"}'}
                   for topic in topics_available]

        dispatcher.utter_message(
            text=f'Bitte wählen Sie ein Thema: {topics_available}', buttons=buttons)

        return []
