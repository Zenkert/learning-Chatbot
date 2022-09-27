import json
import random
import logging
import pandas as pd
from typing import Any, Text, Dict, List

from actions import query_db
from actions.enum_uniques import Id
from actions.actions import get_language_and_response

from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher


logging.basicConfig(filename="exceptions.log", level=logging.DEBUG,
                    format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")


class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_greet']

        dispatcher.utter_message(random.choice(message["greeting"]))
        dispatcher.utter_message(random.choice(message["welcome"]))

        return []


class ActionGoodbye(Action):

    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_goodbye']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionDone(Action):

    def name(self) -> Text:
        return "action_done"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_done']

        dispatcher.utter_message(random.choice(message["done"]))

        if random.choice([True, False]):
            dispatcher.utter_message(random.choice(message["availability"]))

        return []


class ActionRephrase(Action):

    def name(self) -> Text:
        return "action_rephrase"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_rephrase']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionDefault(Action):

    def name(self) -> Text:
        return "action_default"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_default']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionIamaBot(Action):

    def name(self) -> Text:
        return "action_i_am_a_bot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        respond_bot = response_query['action_i_am_a_bot']

        dispatcher.utter_message(random.choice(respond_bot))

        message = response_query['action_show_features']
        message_response = message["options"]

        buttons = [
            {'title': random.choice(
                message["activity"]), 'payload': '/ask_for_suggestion'},
            {'title': random.choice(
                message["direct_topic"]), 'payload': '/user_asks_topic_directly'},
            {'title': random.choice(message["more_option"]),
                'payload': '/more_options'},
            {'title': random.choice(
                message["cancel"]), 'payload': '/user_cancel'}
        ]

        dispatcher.utter_message(
            text=random.choice(
                message_response), buttons=buttons, button_type="vertical")

        return []


class ActionWelcome(Action):

    def name(self) -> Text:
        return "action_welcome"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_welcome']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionThanksFeedback(Action):

    def name(self) -> Text:
        return "action_thanks_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_thanks_feedback']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionFindSubject(Action):

    def name(self) -> Text:
        return "action_find_subject"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_find_subject']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionGreat(Action):

    def name(self) -> Text:
        return "action_great"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_great']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionIWillStop(Action):

    def name(self) -> Text:
        return "action_i_will_stop"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_i_will_stop']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionItIsOkay(Action):

    def name(self) -> Text:
        return "action_it_is_okay"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_it_is_okay']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionHappy(Action):

    def name(self) -> Text:
        return "action_happy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['action_happy']

        dispatcher.utter_message(random.choice(message))

        return []


class ActionGoodTime(Action):

    def name(self) -> Text:
        return "action_good_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        _, response_query = get_language_and_response(tracker)

        message = response_query['good_time']

        dispatcher.utter_message(random.choice(message))

        return []


class ValidateQuestionsForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_feedback_form"

    def validate_feedback(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['validate_feedback']

        dispatcher.utter_message(
            text=f'{random.choice(message)}{slot_value}')

        return {'feedback': slot_value}

    def validate_confirm_feedback(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        if slot_value == 'Yes':
            return {'confirm_feedback': 'Yes'}

        return {'confirm_feedback': None}


class ActionFollowQuestionsForm(Action):

    def name(self) -> Text:
        return "action_follow_questions_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id  # sender id
        subject = tracker.get_slot('subject')  # slot value of subject
        topic = tracker.get_slot('topic')  # slot value of topic

        intent_value = tracker.get_intent_of_latest_message()

        if len(user_id) > Id.TELEGRAM_UUID_LENGTH.value or topic == "STOP":
            return []

        # there are no activities available, so the user returns without completing any activity
        if intent_value == "inform_new":
            return [FollowupAction(name="action_continue")]

        student_data = pd.read_excel(
            'actions/student_db_new.xlsx')  # read data
        student_data = student_data.loc[:, ~
                                        student_data.columns.str.contains('^Unnamed')]  # removing "Unnamed" columns
        try:
            for index, row in student_data.iterrows():  # iterating over rows to find the user
                if str(row['User']) == str(user_id):
                    # Increamenting number of times the user has chosen a subject
                    student_data.loc[index, subject] += 1
                    break  # out of loop once unique user is found

            student_data.to_excel('actions/student_db_new.xlsx', index=False)
        except Exception as e:
            logging.info(e)

        # followup with whether the user wants to continue for the Telegram bot
        if len(tracker.sender_id) < Id.ANDROID_UUID_LENGTH.value:
            return [FollowupAction(name="action_continue")]

        return []


class ActionCancelOption(Action):

    def name(self) -> Text:
        return "action_cancel_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_i_will_stop']

        dispatcher.utter_message(
            text=f'{random.choice(message)}')

        return []
