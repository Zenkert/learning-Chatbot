from datetime import datetime as dt
from pydoc_data.topics import topics
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, UserUtteranceReverted, ActionReverted
from rasa_sdk import Action, Tracker
import pandas as pd
from typing import Any, Text, Dict, List
import json
import random
from bson import ObjectId
#
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions import main, plot
from fuzzywuzzy import process

with open('actions/responses.json', 'r') as file:
    data = json.load(file)

dict_vars = {'total_subs': None, 'total_topicss': None,
             'subject_idx': 0, 'topic_idx': 0, 'i': 0}


class ActionSetLanguage(Action):

    def name(self) -> Text:
        return "action_set_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang1 = tracker.get_slot('language')

        user_lang2 = 'EN' if user_lang1 is None else user_lang1

        # user_ent = 'None'
        # try:
        #     user_ent = next(tracker.get_latest_entity_values('language'))
        # except:
        #     pass

        dispatcher.utter_message(
            text=f'User language is {user_lang1}, {user_lang2}')

        return [SlotSet("language", "EN")]


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

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_ask_subj']

        if dict_vars['subject_idx'] == 0:
            dict_vars['total_subs'], sub_dict = main.get_subjects()
            subs = [dict_vars['total_subs'].pop() for _ in range(6)]
            buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                            for sub in subs]
            buttons_subj.append(
                {"title": message["next"], "payload": '/next_option{"subj":"None"}'})

            _ = [sub_dict.pop(s) for s in subs]

        else:
            subs = []
            try:
                for _ in range(len(dict_vars['total_subs'])):
                    subs.append(dict_vars['total_subs'].pop())
            except:
                pass

            buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                            for sub in subs]

        user_input = tracker.latest_message.get('text')

        fnd, common_value = None, 50

        try:
            subject_list, _ = main.get_subjects()
            fnd, common_value = process.extractOne(
                user_input, subject_list)
            print('dict_vars[\'total_subs\']: ', dict_vars['total_subs'])
            print("fnd: ", fnd, 'common value: ', common_value)
        except:
            pass

        if fnd is not None and not user_input.startswith('/'):

            if common_value >= 70:
                dispatcher.utter_message(f'{message["found"]} {fnd!r}')
                buttons = [{'title': message["yes"], 'payload': '/inform_new{"subj":"'+fnd+'"}'},  # add subject as entity
                           {'title': message["no"], 'payload': '/user_deny{"subj":"None"}'}]
                dispatcher.utter_message(
                    text=f'{message["mean"]}', buttons=buttons)
                return []

            # elif 50 <= common_value < 70 and not user_input.startswith('/'):
            #     dispatcher.utter_message(f'{message["found"]} {fnd!r}')
            #     dispatcher.utter_message(
            #         text=f'{message["mean"]}', buttons=buttons)
            #     return []

        # try:
        #     subject = next(tracker.get_latest_entity_values('subject'))
        # except:
        #     subject = None

        # if subject is not None:
        #     dispatcher.utter_message(
        #         text=f'{message["query"]}: {subject!r}')
        #     print("Subject: ", subject)
        #     print(f'{message["query"]}: {subject!r}')

        message = message["available"]
        try:
            num_times = next(tracker.get_latest_entity_values('num_times'))
            print(f'{num_times = }')
            if num_times == 1:
                message = message["choose"]
        except:
            pass

        dispatcher.utter_message(
            text=message, buttons=buttons_subj, button_type="vertical")

        return []

# class ActionTellSubjects(Action):

#     def name(self) -> Text:
#         return "action_ask_subj"

#     @staticmethod
#     def user_language():
#         pass

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         # name = tracker.get_slot('name')
#         # print('name: ', name)

#         print('subject_idx:', dict_vars['subject_idx'])

#         if dict_vars['subject_idx'] == 0:
#             dict_vars['total_subs'] = main.get_subjects(
#                 collection_name='subjects')
#             subs = [dict_vars['total_subs'].pop() for _ in range(5)]
#             buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
#                             for sub in subs]
#             buttons_subj.append(
#                 {"title": 'Next', "payload": '/next_option{"subj":"None"}'})

#         elif dict_vars['subject_idx'] != 0:
#             if len(dict_vars['total_subs']) >= 5:
#                 subs = [dict_vars['total_subs'].pop() for _ in range(5)]
#                 buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
#                                 for sub in subs]
#                 buttons_subj.append(
#                     {"title": 'Next', "payload": '/next_option{"subj":"None"}'})

#             else:
#                 subs = [dict_vars['total_subs'].pop()
#                         for _ in range(len(dict_vars['total_subs']))]
#                 buttons_subj = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
#                                 for sub in subs]

#         try:
#             subject = next(tracker.get_latest_entity_values('subject'))
#         except:
#             subject = None

#         if subject is not None:
#             fnd, common_value = process.extractOne(subject, subs)
#             print("fnd: ", fnd, 'common value: ', common_value)
#             buttons = [{'title': 'Yes', 'payload': '/inform_new{"subj":"'+fnd+'"}'},  # add subject as entity
#                        {'title': 'No', 'payload': '/user_deny{"subj":"None"}'}]
#             dispatcher.utter_message(
#                 text=f"I found {fnd!r} in my database. Is that what you mean?", buttons=buttons)
#             print("Subject: ", subject)

#         else:
#             dispatcher.utter_message(
#                 text=f"These are the subjects available. Please choose one:", buttons=buttons_subj, button_type="vertical")

#         return []


class ActionGiveSuggestion(Action):

    def name(self) -> Text:
        return "action_give_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_give_suggestion']

        subs = main.get_subjects(collection_name='subjects')

        buttons = [{"title": sub, "payload": '/inform_new{"subj":"'+sub+'"}'}
                   for sub in subs]

        dispatcher.utter_message(
            text=message, buttons=buttons)

        return []


class ActionTellTopics(Action):

    def name(self) -> Text:
        return "action_ask_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_ask_topic']

        subject = tracker.get_slot('subj')

        if dict_vars['topic_idx'] == 0:
            dict_vars['total_topics'], topic_dict = main.get_topics(subject)

            if len(dict_vars['total_topics']) == 0:
                dispatcher.utter_message(text=message['not_available'])
                return [SlotSet('topic', 'NOT AVAILABLE'), SlotSet('question', 'NOT AVAILABLE')]

            elif len(dict_vars['total_topics']) <= 6:
                topics = [dict_vars['total_topics'].pop()
                          for _ in range(len(dict_vars['total_topics']))]

            else:
                topics = [dict_vars['total_topics'].pop()
                          for _ in range(6)]

            buttons = [{"title": topic, "payload": '/inform_new{"topic":"'+topic_id+'"}'}
                       for topic, topic_id in topic_dict.items()]

            if len(topics) >= 6:
                buttons.append(
                    {"title": message["next"], "payload": '/next_option{"topic":"None"}'})

            _ = [topic_dict.pop(s) for s in topics]

        else:
            topics = [dict_vars['total_topics'].pop()
                      for _ in range(len(dict_vars['total_topics']))]
            buttons = [{"title": topic, "payload": '/inform_new{"topic":"'+topic_id+'"}'}
                       for topic, topic_id in topic_dict.items()]

        # ===============   WORKING   ================

        # topic_list, topics_available = main.get_topics(subject)
        # buttons = [{"title": topic, "payload": '/inform_new{"topic":"'+topic_id+'"}'}
        #         for topic, topic_id in topics_available.items()]

        # dispatcher.utter_message(
        #     text=f'{message}', buttons=buttons, button_type="vertical")

        dispatcher.utter_message(
            text=message['topic'], buttons=buttons, button_type="vertical")

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

        if intent_value == "next_option":
            dict_vars['subject_idx'] += 1
            return {'subj': None}
        elif intent_value == "user_deny":
            return {'subj': None}

        dict_vars['subject_idx'] = 0
        return {'subj': slot_value}

    def validate_topic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        intent_value = tracker.get_intent_of_latest_message()

        if intent_value == "next_option":
            dict_vars['topic_idx'] += 1
            return {'topic': None}
        elif intent_value == "user_deny":
            return {'topic': None}

        dict_vars['topic_idx'] = 0

        if len(tracker.sender_id) == main.ID.TELEGRAM_UUID_LENGTH.value:
            return {'topic': slot_value, 'question': None}

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


# class ActionAskQuestion(Action):

#     def name(self) -> Text:
#         return "action_ask_question"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         topic_id = tracker.get_slot('topic')
#         print('topic_id: ', topic_id)

#         question_count, questions_available = main.get_questions(topic_id)

#         if question_count == 0:
#             dispatcher.utter_message(
#                 text='Sorry, there are no activities available for this topic yet!')
#             dispatcher.utter_message(text='We will add new activities soon.')

#         mcq_question = questions_available['mcq_question'][dict_vars['i']]
#         mcq_choices = questions_available['mcq_choices'][dict_vars['i']]
#         print('i: ', dict_vars['i'], 'mcq_qq: ', mcq_question)
#         buttons = [{"title": choice, "payload": f"option{idx+1}"}
#                    for idx, choice in enumerate(mcq_choices)]

#         dispatcher.utter_message(
#             text=mcq_question, buttons=buttons, button_type="vertical")

#         return []

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

#         topic_id = tracker.get_slot('topic')
#         question_count, questions_available = main.get_questions(topic_id)

#         right_answer = questions_available['right_answer'][dict_vars['i']]
#         pos_feedback = questions_available['feedback']['pos_feedback'][dict_vars['i']]
#         neg_feedback = questions_available['feedback']['neg_feedback'][dict_vars['i']]
#         # mcq_choices = questions_available['mcq_choices'][dict_vars['i']]

#         if slot_value.startswith('/inform_new'):
#             return {'question': None}
#         elif slot_value == right_answer:
#             dispatcher.utter_message(text=pos_feedback)
#         else:
#             dispatcher.utter_message(text=neg_feedback)

#         if dict_vars['i'] < question_count-1:
#             dict_vars['i'] += 1
#             print('i ==> ', dict_vars['i'],
#                   'question_count ==> ', question_count)
#             return {'question': None}
#         dict_vars['i'] = 0  # reset value of i to loop again

#         return {'question': slot_value}


class ActionSetReminder(Action):

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        reminder_time = None

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_set_reminder']

        try:
            reminder_time = next(tracker.get_latest_entity_values('time'))
        except:
            pass

        if reminder_time == 'None' or reminder_time == None:
            dispatcher.utter_message(text=message["time"])
            return []

        time_object = dt.strptime(reminder_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        print(f'{time_object=}')
        dispatcher.utter_message(
            f'{message["remind"]} {time_object.time()} {message["on"]} {time_object.date()}.')

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

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_react_to_reminder']

        dispatcher.utter_message(text=message)

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

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_forget_reminders']

        dispatcher.utter_message(text=message)

        return [ReminderCancelled()]


class ActionGiveProgress(Action):

    def name(self) -> Text:
        return "action_give_progress"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_give_progress']

        dispatcher.utter_message(
            text=message["message1"])

        final_path, image_url = plot.image_url(current_time=dt.now())
        print(f'{image_url = }')
        print(f'{final_path = }')
        dispatcher.utter_message(
            text=f'{message["message2"]}:', image=image_url)

        return []


class ActionGiveImprovement(Action):

    def name(self) -> Text:
        return "action_give_improvement"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        import socket

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_give_improvement']

        dispatcher.utter_message(
            text=f"{message}: {socket.gethostname()}")

        return []


class ActionGiveApproach(Action):

    def name(self) -> Text:
        return "action_give_approach"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_give_approach']

        dispatcher.utter_message(text=message)

        return []


class ActionGetFeedback(Action):

    def name(self) -> Text:
        return "action_get_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_get_feedback']

        dispatcher.utter_message(text=message)

        return []


class ActionAskFeedback(Action):

    def name(self) -> Text:
        return "action_ask_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_ask_feedback']

        message_list = [message["choice1"], message["choice2"]]

        dispatcher.utter_message(text=random.choice(message_list))

        return []


class ActionAskConfirmFeedback(Action):

    def name(self) -> Text:
        return "action_ask_confirm_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_ask_confirm_feedback']

        if tracker.latest_message['text'] == 'No':
            return [ActionReverted(), SlotSet('feedback', None)]

        buttons = [{'title': message["yes"], 'payload': 'Yes'},
                   {'title': message["no"], 'payload': 'No'}]

        dispatcher.utter_message(
            text=message["confirm"], buttons=buttons, button_type="vertical")

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

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['validate_feedback']

        dispatcher.utter_message(
            text=f'{message}{slot_value}')

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

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_show_features']

        if tracker.get_intent_of_latest_message() == "start":
            message = message["start"]

        buttons = [{'title': message["activity"], 'payload': '/ask_for_suggestion'},
                   {'title': message["subject"],
                       'payload': '/find_subject'},
                   {'title': message["question_types"],
                       'payload': '/ask_question_types'},
                   {'title': message["progress"],
                       'payload': '/ask_progress'},
                   {'title': message["improve"],
                       'payload': '/ask_improvement'},
                   {'title': message["approach"],
                       'payload': '/ask_approach'},
                   {'title': message["reminder"],
                       'payload': '/ask_remind_call{"time":"None"}'},
                   {'title': message["cancel_reminder"],
                       'payload': '/ask_forget_reminders'},
                   {'title': message["feedback"],
                       'payload': '/user_feedback'},
                   {'title': message["bot"], 'payload': '/bot_challenge'}
                   ]
        dispatcher.utter_message(
            text=message["options"], buttons=buttons, button_type="vertical")

        return []


class ActionExplainQuestionTypes(Action):

    def name(self) -> Text:
        return "action_explain_question_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        ANDROID_UUID_LENGTH = 16

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_explain_question_types']

        if len(tracker.sender_id) < ANDROID_UUID_LENGTH:
            buttons = [
                {'title': message["1"], 'payload': '/ask_types{"type":"MCQ"}'},
                {'title': message["2"],
                 'payload': '/ask_types{"type":"True_False"}'}
            ]
        else:
            buttons = [
                {'title': message["1"], 'payload': '/ask_types{"type":"MCQ"}'},
                {'title': message["2"],
                    'payload': '/ask_types{"type":"True_False"}'},
                {'title': message["3"],
                    'payload': '/ask_types{"type":"Matching_Pairs"}'},
                {'title': message["4"],
                    'payload': '/ask_types{"type":"Open_ended"}'}
            ]

        dispatcher.utter_message(
            text=message["question"], buttons=buttons, button_type="vertical")

        return []


class ActionExplainQuestionTypesDefinition(Action):

    def name(self) -> Text:
        return "action_explain_question_types_definition"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_explain_question_types_definition']

        entity = tracker.get_slot('type')

        dispatcher.utter_message(text=f'Entity is {entity}')
        explanation = {"MCQ": message["MCQ"],
                       "True_False": message["True_False"],
                       "Matching_Pairs": message["Matching_Pairs"],
                       "Open_ended": message["Open_ended"]}

        # explanation = {message["1"]: message["MCQ"],
        #                message["2"]: message["True_False"],
        #                message["3"]: message["Matching_Pairs"]}

        if entity is not None:
            message = explanation[entity]
        else:
            message = "Sorry, I'm facing a problem right now!"
        dispatcher.utter_message(text=message)

        return []


class ActionContinue(Action):

    def name(self) -> Text:
        return "action_continue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_lang = tracker.get_slot('language')

        user_lang = 'EN' if user_lang is None else user_lang

        message = data['language'][user_lang]['action_continue']

        question = tracker.get_slot('question')
        print(f'{question = }')
        if question == 'NOT AVAILABLE' or question.startswith('/inform_new'):
            print(f'Inside {question = }')
        else:
            dispatcher.utter_message(text=message["continue"])

        buttons = [
            {'title': message["yes"],
                'payload': '/ask_for_suggestion{"num_times": 1}'},
            {'title': message["no"], 'payload': '/user_done'},
        ]

        dispatcher.utter_message(
            text=message["one_more"], buttons=buttons, button_type="vertical")

        return []
