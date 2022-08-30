from email.mime import image
from time import time
from urllib import response
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, UserUtteranceReverted, ActionReverted
from rasa_sdk import Action, Tracker
import pandas as pd
from typing import Any, Text, Dict, List
import time
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

        if len(tracker.sender_id) != main.ID.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(response="utter_good_time")
            return [SlotSet("question", "ANDROID APP")]

        question_count, questions_available = main.get_questions(topic_id)
        print(f'{question_count = }')
        if question_count == 0:
            dispatcher.utter_message(
                text='Sorry, there are no activities available for this topic yet!')
            dispatcher.utter_message(text='We will add new activities soon.')
            return [SlotSet('question', 'NOT AVAILABLE')]

        mcq_question = questions_available['mcq_question'][dict_vars['i']].pop(
            0)
        mcq_choices = questions_available['mcq_choices'][dict_vars['i']].pop(0)
        file = questions_available['file'][dict_vars['i']].pop(0)

        buttons = [{"title": choice, "payload": f"option{idx+1}"}
                   for idx, choice in enumerate(mcq_choices)]

        buttons_new = []
        true_false_question_type = False

        for idx, choice in enumerate(mcq_choices):
            if choice == 'True' or choice == 'False':
                true_false_question_type = True
                buttons_new.append({"title": choice, "payload": choice})

        if file != '':
            split_file = file.split('5000')
            secure_link = 'https://goy0tnphpd.execute-api.eu-central-1.amazonaws.com'
            secure_file_url = secure_link+split_file[1]

        # file = 'https://goy0tnphpd.execute-api.eu-central-1.amazonaws.com/api/openEnded/getImage/1660826908189mona_lisa,_by_leonardo_da_vinci,_from_c2rmf_retouched.jpg'

        # dispatcher.utter_message(image=secure_file_url)
        # dispatcher.utter_message(text=mcq_question)

        if true_false_question_type:
            if file == '':
                dispatcher.utter_message(
                    text=mcq_question, buttons=buttons_new, button_type="vertical")
            else:
                dispatcher.utter_message(text=mcq_question, image=secure_file_url,
                                         buttons=buttons_new, button_type="vertical")

        else:
            if file == '':
                dispatcher.utter_message(
                    text=mcq_question, buttons=buttons, button_type="vertical")
            else:
                dispatcher.utter_message(
                    text=mcq_question, image=secure_file_url, buttons=buttons, button_type="vertical")

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

        right_answer = questions_available['right_answer'][dict_vars['i']].pop(
            0)
        pos_feedback = questions_available['feedback']['pos_feedback'][dict_vars['i']].pop(
            0)
        neg_feedback = questions_available['feedback']['neg_feedback'][dict_vars['i']].pop(
            0)

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

        user_id = tracker.sender_id  # sender ID
        subject = tracker.get_slot('subj')  # slot value of subject

        student_data = pd.read_excel(
            'actions/student_db_new.xlsx')  # read data

        try:
            for index, row in student_data.iterrows():  # iterating over rows
                if str(row['User']) == str(user_id):
                    student_data.loc[student_data['User']
                                     == user_id, subject] += 1  # Increamenting number of times the user has chosen a subject
                    break  # out of loop once unique user is found

            student_data.to_excel('actions/student_db_new.xlsx', index=False)
        except:
            pass

        if len(tracker.sender_id) == main.ID.TELEGRAM_UUID_LENGTH.value:
            return [FollowupAction(name="action_continue")]

        return []
