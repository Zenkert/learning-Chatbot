from unittest import result
from urllib import response
import pandas as pd
from typing import Any, Text, Dict, List
import json
import random

from actions import main
from actions.actions import get_language_and_response
from actions.enum_uniques import ID
#
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, UserUtteranceReverted, ActionReverted
from rasa_sdk import Action, Tracker


with open('actions/responses.json', 'r') as file:
    data = json.load(file)

# dict_vars = {'subject_idx': 0, 'topic_idx': 0, 'idx': 0}


# class ActionAskQuestion(Action):

#     def name(self) -> Text:
#         return "action_ask_question"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         user_language, response_query = get_language_and_response(tracker)

#         message = response_query['validate_question']

#         topic_id = tracker.get_slot('topic')

#         # Base condition to check if Telegram user or Android user
#         if len(tracker.sender_id) > ID.TELEGRAM_UUID_LENGTH.value:
#             dispatcher.utter_message(text=random.choice(
#                 response_query["good_time"]))
#             return [SlotSet("question", "ANDROID APP")]

#         question_count, questions_available = main.get_questions(topic_id)

#         if question_count == 0:
#             dispatcher.utter_message(
#                 text=random.choice(message["sorry"]))
#             dispatcher.utter_message(text=random.choice(message["add_soon"]))
#             return [SlotSet('question', 'NOT AVAILABLE')]

#         sender_id = tracker.sender_id
#         # if sender_idx := dict_vars.get(sender_id, None) == None:
#         #     dict_vars[sender_id] = 0

#         print(dict_vars)

#         mcq_question = questions_available['mcq_question'][dict_vars[sender_id]].pop(
#             0)
#         mcq_choices = questions_available['mcq_choices'][dict_vars[sender_id]].pop(
#             0)
#         file = questions_available['file'][dict_vars[sender_id]].pop(0)

#         buttons = [{"title": choice, "payload": f"option{idx+1}"}
#                    for idx, choice in enumerate(mcq_choices)]

#         # mcq_question = questions_available['mcq_question'][dict_vars['idx']].pop(
#         #     0)
#         # mcq_choices = questions_available['mcq_choices'][dict_vars['idx']].pop(
#         #     0)
#         # file = questions_available['file'][dict_vars['idx']].pop(0)

#         # buttons = [{"title": choice, "payload": f"option{idx+1}"}
#         #            for idx, choice in enumerate(mcq_choices)]

#         buttons_new = []
#         true_false_question_type = False

#         message_2 = response_query['action_ask_question']

#         for idx, choice in enumerate(mcq_choices):
#             if choice == 'True' or choice == 'False':
#                 true_false_question_type = True
#                 buttons_new.append({"title": random.choice(
#                     message_2["true"]), "payload": "true"})
#                 buttons_new.append({"title": random.choice(
#                     message_2["false"]), "payload": "false"})

#                 break

#         if file != '':
#             split_file = file.split('5000')
#             secure_link = 'https://goy0tnphpd.execute-api.eu-central-1.amazonaws.com'
#             secure_file_url = secure_link+split_file[1]

#         # file = 'https://goy0tnphpd.execute-api.eu-central-1.amazonaws.com/api/openEnded/getImage/1660826908189mona_lisa,_by_leonardo_da_vinci,_from_c2rmf_retouched.jpg'

#         # dispatcher.utter_message(image=secure_file_url)
#         # dispatcher.utter_message(text=mcq_question)

#         if true_false_question_type:
#             if file == '':
#                 dispatcher.utter_message(
#                     text=mcq_question, buttons=buttons_new, button_type="vertical")
#             else:
#                 dispatcher.utter_message(text=mcq_question, image=secure_file_url,
#                                          buttons=buttons_new, button_type="vertical")

#         else:
#             if file == '':
#                 dispatcher.utter_message(
#                     text=mcq_question, buttons=buttons, button_type="vertical")
#             else:
#                 dispatcher.utter_message(
#                     text=mcq_question, image=secure_file_url, buttons=buttons, button_type="vertical")

#         return []


# class ValidateQuestionsForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_questions_form"

#     def validate_question(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict
#     ) -> Dict[Text, Any]:

#         user_language, response_query = get_language_and_response(tracker)

#         message = response_query['validate_question']

#         sender_id = tracker.sender_id

#         if len(sender_id) > ID.TELEGRAM_UUID_LENGTH.value:
#             dispatcher.utter_message(random.choice(
#                 response_query["good_time"]))
#             return {'question': 'ANDROID_APP'}

#         topic_id = tracker.get_slot('topic')
#         question_count, questions_available = main.get_questions(
#             topic_id)

#         if question_count == 0:
#             dispatcher.utter_message(
#                 text=random.choice(message["sorry"]))
#             dispatcher.utter_message(text=random.choice(message["add_soon"]))
#             return [SlotSet('question', 'NOT AVAILABLE')]

#         # if sender_idx := dict_vars.get('sender_id', None) == None:
#         #     dict_vars[sender_id] = 0

#         print(dict_vars)

#         if slot_value.startswith('/inform_new'):
#             return {'question': None}

#         right_answer = questions_available['right_answer'][dict_vars[sender_id]].pop(
#             0)
#         pos_feedback = questions_available['feedback']['pos_feedback'][dict_vars[sender_id]].pop(
#             0)
#         neg_feedback = questions_available['feedback']['neg_feedback'][dict_vars[sender_id]].pop(
#             0)

#         if slot_value.startswith('/inform_new'):
#             return {'question': None}
#         elif slot_value.lower() == right_answer.lower():
#             dispatcher.utter_message(text=pos_feedback)
#         else:
#             dispatcher.utter_message(text=neg_feedback)

#         print('++++++++++++++++++++question_count-1: ', question_count-1, type(question_count-1),
#               'dict_vars[sender_id]: ', dict_vars[sender_id], type(dict_vars[sender_id]))
#         if dict_vars[sender_id] < question_count-1:
#             print('++++++++++++++++++++It is WORKING')
#             dispatcher.utter_message(text='It is WORKING')
#             dict_vars[sender_id] += 1
#             return {'question': None}

#         # dict_vars['idx'] = 0  # reset value of idx for the next interaction
#         dict_vars[sender_id] = 0

#         return {'question': 'FILLED'}


class ActionFollowQuestionsForm(Action):

    def name(self) -> Text:
        return "action_follow_questions_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id  # sender ID
        subject = tracker.get_slot('subject')  # slot value of subject

        if len(user_id) > ID.TELEGRAM_UUID_LENGTH.value:
            return []

        student_data = pd.read_excel(
            'actions/student_db_new.xlsx')  # read data
        student_data = student_data.loc[:, ~
                                        student_data.columns.str.contains('^Unnamed')]  # removing "Unnamed" column
        try:
            for index, row in student_data.iterrows():  # iterating over rows
                if str(row['User']) == str(user_id):
                    # Increamenting number of times the user has chosen a subject
                    student_data.loc[index, subject] += 1
                    break  # out of loop once unique user is found

            student_data.to_excel('actions/student_db_new.xlsx', index=False)
        except:
            pass

        if len(tracker.sender_id) < ID.ANDROID_UUID_LENGTH.value:
            return [FollowupAction(name="action_continue")]

        return []


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

        message = response_query['action_i_am_a_bot']

        dispatcher.utter_message(random.choice(message))

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
