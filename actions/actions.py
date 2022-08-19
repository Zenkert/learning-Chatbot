from datetime import datetime as dt
from email import message
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, UserUtteranceReverted, ActionReverted
from rasa_sdk import Action, Tracker
import pandas as pd
from typing import Any, Text, Dict, List
import json
import random
from bson import ObjectId

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions import main, plot
from fuzzywuzzy import process
from dateutil.parser import *

dict_vars = {'total_subs': None, 'subject_idx': 0, 'topic_idx': 0, 'i': 0}


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
        return "action_ask_subj"

    @staticmethod
    def user_language():
        pass

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # name = tracker.get_slot('name')
        # print('name: ', name)

        print('subject_idx:', dict_vars['subject_idx'])

        if dict_vars['subject_idx'] == 0:
            dict_vars['total_subs'] = main.get_subjects(
                collection_name='subjects')
            subs = [dict_vars['total_subs'].pop() for _ in range(5)]
            buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                            for sub in subs]
            buttons_subj.append(
                {"title": 'Next', "payload": '/next_option{"subj":"None"}'})

        elif dict_vars['subject_idx'] != 0:
            if len(dict_vars['total_subs']) >= 5:
                subs = [dict_vars['total_subs'].pop() for _ in range(5)]
                buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                                for sub in subs]
                buttons_subj.append(
                    {"title": 'Next', "payload": '/next_option{"subj":"None"}'})

            else:
                subs = [dict_vars['total_subs'].pop()
                        for _ in range(len(dict_vars['total_subs']))]
                buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                                for sub in subs]

        user_input = tracker.latest_message.get('text')

        fnd, common_value = process.extractOne(user_input, subs)
        print("fnd: ", fnd, 'common value: ', common_value)

        buttons = [{'title': 'Yes', 'payload': '/inform_new{"subj":"'+fnd+'"}'},  # add subject as entity
                   {'title': 'No', 'payload': '/user_deny{"subj":"None"}'}]

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
            subject = next(tracker.get_latest_entity_values('subject'))
        except:
            subject = None

        if subject is not None:
            dispatcher.utter_message(
                text=f"I will query my database about {subject}")
            print("Subject: ", subject)
            print(f"I will query my database about {subject}")

        else:
            dispatcher.utter_message(
                text=f"These are some of the subjects available.", buttons=buttons_subj, button_type="vertical")

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
        return "action_ask_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subject = tracker.get_slot('subj')
        print('subj -> action_tell_topics: ', subject)

        # if topic_idx == 0:
        topics_available = main.get_topics(subject)
        buttons = [{"title": topic, "payload": '/inform_new{"topic":"'+topic_id+'"}'}
                   for topic, topic_id in topics_available.items()]

        dispatcher.utter_message(
            text=f'Please select a topic: ', buttons=buttons, button_type="vertical")

        return []


class ValidateSubmitWithTopicForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_subject_with_topic_form"

    def validate_subj(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        intent_value = tracker.get_intent_of_latest_message()

        print('intent_value: ', intent_value)

        print('slot_valuexx->>', slot_value)

        if intent_value == "next_option":
            dict_vars['subject_idx'] += 1
            return {'subj': None}
        elif intent_value == "user_deny":
            return {'subj': None}

        print(f"{dict_vars['subject_idx'] = }")
        dict_vars['subject_idx'] = 0
        return {'subj': slot_value}

    def validate_topic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        return {'topic': slot_value}


class ActionCleanEntity(Action):

    def name(self) -> Text:
        return "action_clean_entity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # reset dict before activation of form

        dict_vars['i'] = 0
        dict_vars['subject_idx'] = 0

        return [SlotSet("subj", None), SlotSet("topic", None)]


class ActionCleanFeedbackformSlots(Action):

    def name(self) -> Text:
        return "action_clean_feedbackform_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("feedback", None), SlotSet("confirm_feedback", None)]


class ActionAskQuestion(Action):

    def name(self) -> Text:
        return "action_ask_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic_id = tracker.get_slot('topic')
        print('topic_id: ', topic_id)

        _, questions_available = main.get_questions(topic_id)

        mcq_question = questions_available['mcq_question'][dict_vars['i']]
        mcq_choices = questions_available['mcq_choices'][dict_vars['i']]
        print('i: ', dict_vars['i'], 'mcq_qq: ', mcq_question)
        buttons = [{"title": choice, "payload": f"option{idx+1}"}
                   for idx, choice in enumerate(mcq_choices)]

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

        topic_id = tracker.get_slot('topic')
        question_count, questions_available = main.get_questions(topic_id)

        right_answer = questions_available['right_answer'][dict_vars['i']]
        pos_feedback = questions_available['feedback']['pos_feedback'][dict_vars['i']]
        neg_feedback = questions_available['feedback']['neg_feedback'][dict_vars['i']]
        # mcq_choices = questions_available['mcq_choices'][dict_vars['i']]

        if slot_value.startswith('/inform_new'):
            return {'question': None}
        elif slot_value == right_answer:
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

# class ActionTellSubjects(Action):

#     def name(self) -> Text:
#         return "action_ask_subj"

#     @staticmethod
#     def user_language():
#         pass

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         name = tracker.get_slot('name')
#         print('name: ', name)

#         subs = main.get_subjects(collection_name='subjects')

#         user_input = tracker.latest_message.get('text')

#         fnd, common_value = process.extractOne(user_input, subs)
#         print("fnd: ", fnd, 'common value: ', common_value)

#         buttons = [{'title': 'Yes', 'payload': '/user_affirm{"subj":"'+fnd+'"}'},  # add subject as entity
#                    {'title': 'No', 'payload': '/user_deny'}]

#         if fnd is not None:

#             if common_value >= 70:
#                 dispatcher.utter_message(
#                     text=f"I found {fnd!r} in my database. Is that what you mean?", buttons=buttons)
#                 return []

#             elif 50 <= common_value < 70:
#                 dispatcher.utter_message(
#                     text=f"I think this is the one: {fnd}. Is this what you mean?", buttons=buttons)
#                 return []

#         try:
#             subject = next(tracker.get_latest_entity_values(
#                 entity_type="subject"))
#         except:
#             subject = None

#         if subject is not None:
#             dispatcher.utter_message(
#                 text=f"I will query my database about {subject}")
#             print("Subject: ", subject)
#             print(f"I will query my database about {subject}")

#         else:
#             buttons = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
#                        for sub in subs]

#             dispatcher.utter_message(
#                 text=f"I couldn't find anything related to that subject. These are some of the subjects available.", buttons=buttons)

#         return []


class ActionSetReminder(Action):

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        reminder_time = tracker.get_slot("time")

        if reminder_time == 'None' or reminder_time == None:
            dispatcher.utter_message('Please provide a time!')
            return []

        time_object = dt.strptime(reminder_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        print(f'{time_object=}')
        dispatcher.utter_message(
            f"Okay, I will remind you at {time_object.time()} on {time_object.date()}.")

        entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=time_object,
            entities=entities,
            name="my_reminder",
            kill_on_user_message=False,
        )

        return [reminder]


class ActionReactToReminder(Action):

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(f"Hey, here is your reminder!")

        return []


class ActionCleanTimeSlot(Action):

    def name(self) -> Text:
        return "action_clean_time_slot"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [SlotSet('time', None)]


class ForgetReminders(Action):

    def name(self) -> Text:
        return "action_forget_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Okay, I'll cancel your reminders.")

        return [ReminderCancelled()]


class ActionGiveProgress(Action):

    def name(self) -> Text:
        return "action_give_progress"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text='Please wait a moment!')

        final_path, image_url = plot.image_url(current_time=dt.now())
        print(f'{image_url = }')
        dispatcher.utter_message(
            text=f'Hey, here is your progress!: {final_path}', image=image_url)

        return []


class ActionGiveImprovement(Action):

    def name(self) -> Text:
        return "action_give_improvement"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text='These are the topics you should improve on!')

        return []


class ActionGiveApproach(Action):

    def name(self) -> Text:
        return "action_give_approach"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text='Please watch the video to get a better understanding :)')

        return []


class ActionGetFeedback(Action):

    def name(self) -> Text:
        return "action_get_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message('Thank you for your input!')

        return []


class ActionAskFeedback(Action):

    def name(self) -> Text:
        return "action_ask_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = ["I would like to hear it. Please provide your input in one complete message!",
                   "Oh, please provide your input in one complete message!"]

        dispatcher.utter_message(text=random.choice(message))

        return []


class ActionAskConfirmFeedback(Action):

    def name(self) -> Text:
        return "action_ask_confirm_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.latest_message['text'] == 'No':
            return [ActionReverted(), SlotSet('feedback', None)]

        buttons = [{'title': 'Yes, proceed!👍', 'payload': 'Yes'},
                   {'title': 'No, I want to make changes👎', 'payload': 'No'}]

        dispatcher.utter_message(
            text='Are you sure you want to submit?', buttons=buttons, button_type="vertical")

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

        dispatcher.utter_message(
            text=f'Your input is: {slot_value}')

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


class ActionShowFeatures(Action):

    def name(self) -> Text:
        return "action_show_features"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = 'Here are some of the options you can choose from:'

        if tracker.get_intent_of_latest_message() == "start":
            message = 'Welcome. I am a bot and I\'m here to assist you in your studies. You can choose an option from below to start!'

        buttons = [{'title': 'Do an activity', 'payload': '/ask_for_suggestion'},
                   {'title': 'Ask for a subject', 'payload': '/find_subject'},
                   {'title': 'Question types available',
                       'payload': '/ask_question_types'},
                   {'title': 'What is my progress?', 'payload': '/ask_progress'},
                   {'title': 'What should I improve?',
                       'payload': '/ask_improvement'},
                   {'title': 'Show me how to solve activities',
                       'payload': '/ask_approach'},
                   {'title': 'Create a reminder',
                       'payload': '/ask_remind_call{"time":None}'},
                   {'title': 'Cancel my reminders',
                       'payload': '/ask_forget_reminders'},
                   {'title': 'I want to give feedback',
                       'payload': '/user_feedback'},
                   {'title': 'Who are you?', 'payload': '/bot_challenge'},
                   {'title': '', 'payload': '/'}
                   ]
        dispatcher.utter_message(
            text=message, buttons=buttons, button_type="vertical")

        return []


class ActionExplainQuestionTypes(Action):

    def name(self) -> Text:
        return "action_explain_question_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = 'These are the question types available. Please select an option to learn more'

        buttons = [
            {'title': 'MCQ', 'payload': '/inform{"type":"MCQ"}'},
            {'title': 'True/False', 'payload': '/inform{"type":"True/False"}'},
            {'title': 'Matching Pairs', 'payload': '/inform{"type":"Matching Pairs"}'}
        ]

        dispatcher.utter_message(
            text=message, buttons=buttons, button_type="vertical")

        return []


class ActionExplainQuestionTypesDefinition(Action):

    def name(self) -> Text:
        return "action_explain_question_types_definition"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entity = next(tracker.get_latest_entity_values('type'))

        explanation = {'MCQ': 'A multiple-choice question(MCQ) is composed of two parts: a stem that identifies the question or problem, and a set of alternatives or possible answers that contain a key that is the best answer to the question, and a number of distractors that are plausible but incorrect answers to the question.',
                       'True/False': 'True/false determines whether a statement is correct. You have a 50-50 chance of guessing the correct answer',
                       'Matching Pairs': 'Matching pairs consist of two lists of items. For each item in List A, there is an item in List B that\'s related. Find the related pairs'}

        message = explanation[entity]
        dispatcher.utter_message(text=message)

        return []
