from urllib import response
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, UserUtteranceReverted, ActionReverted
from rasa_sdk import Action, Tracker
import pandas as pd
from typing import Any, Text, Dict, List
import json
#
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions import main

dict_vars = {'total_subs': None, 'total_topicss': None,
             'subject_idx': 0, 'topic_idx': 0, 'i': 0}


class ActionAskQuestion(Action):

    def name(self) -> Text:
        return "action_ask_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic_id = tracker.get_slot('topic')

        if len(tracker.sender_id) > main.ID.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(response="utter_good_time")
            return [SlotSet("question", "ANDROID APP")]

        question_count, questions_available = main.get_questions(topic_id)
        print(f'{question_count = }')
        if question_count == 0:
            dispatcher.utter_message(
                text='Sorry, there are no activities available for this topic yet!')
            dispatcher.utter_message(text='We will add new activities soon.')
            return [SlotSet('question', 'NOT AVAILABLE')]

        mcq_question = questions_available['mcq_question'][dict_vars['i']]
        mcq_choices = questions_available['mcq_choices'][dict_vars['i']]
        print('i: ', dict_vars['i'], 'mcq_qq: ', mcq_question)
        buttons = [{"title": choice, "payload": f"option{idx+1}"}
                   for idx, choice in enumerate(mcq_choices)]

        buttons_new = []
        true_false_question_type = False

        for idx, choice in enumerate(mcq_choices):
            if choice == 'True' or choice == 'False':
                true_false_question_type = True
                buttons_new.append({"title": choice, "payload": choice})

        if true_false_question_type:
            dispatcher.utter_message(
                text=mcq_question, buttons=buttons_new, button_type="vertical")
        else:
            dispatcher.utter_message(
                text=mcq_question, buttons=buttons, button_type="vertical")

        return []


class ValidateQuestionsForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_questions_form"

    def validate_question(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        if len(tracker.sender_id) != main.ID.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(response="utter_good_time")
            return {'question': slot_value}

        topic_id = tracker.get_slot('topic')
        question_count, questions_available = main.get_questions(topic_id)

        if question_count == 0:
            dispatcher.utter_message(
                text='Sorry, there are no activities available for this topic yet!')
            dispatcher.utter_message(text='We will add new activities soon.')
            return [SlotSet('question', 'NOT AVAILABLE')]

        right_answer = questions_available['right_answer'][dict_vars['i']]
        pos_feedback = questions_available['feedback']['pos_feedback'][dict_vars['i']]
        neg_feedback = questions_available['feedback']['neg_feedback'][dict_vars['i']]
        # mcq_choices = questions_available['mcq_choices'][dict_vars['i']]
        print('slot:', slot_value, 'right:', right_answer)
        if slot_value.startswith('/inform_new'):
            return {'question': None}
        elif slot_value.lower() == right_answer.lower():
            dispatcher.utter_message(text=pos_feedback)
        else:
            dispatcher.utter_message(text=neg_feedback)

        if dict_vars['i'] < question_count-1:
            dict_vars['i'] += 1
            print('i ==> ', dict_vars['i'],
                  'question_count ==> ', question_count)
            return {'question': None}
        dict_vars['i'] = 0  # reset value of i to loop again

        return {'question': slot_value}


class ActionFollowQuestionsForm(Action):

    def name(self) -> Text:
        return "action_follow_questions_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(f'{main.ID.TELEGRAM_UUID_LENGTH.value = }')

        if len(tracker.sender_id) == main.ID.TELEGRAM_UUID_LENGTH.value:
            print(f'{len(tracker.sender_id) = }')
            return [FollowupAction(name="action_continue")]

        return []

# class ActionSubmit(Action):

#     def name(self) -> Text:
#         return "action_submit"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         tracker_events = tracker.events

#         transcript = []

#         for data in tracker_events:
#             m = 1
#             if data['event'] == 'user':
#                 try:
#                     user_uttered = data['text']
#                     user_uttered_formatted = f'User: {user_uttered}'
#                     transcript.append(user_uttered_formatted)
#                 except KeyError:
#                     pass

#             elif data['event'] == 'bot':
#                 try:
#                     bot_uttered = data['text']
#                     user_uttered_formatted = f'Bot: {bot_uttered}'
#                     transcript.append(user_uttered_formatted)
#                 except KeyError:
#                     pass

#         dj = pd.DataFrame(transcript, columns=['Transcript'])
#         dj.to_excel('user_transcript.xlsx')

#         return []
