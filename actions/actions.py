from datetime import datetime as dt
from urllib import response
import pandas as pd
from typing import Any, Text, Dict, List
import json
import random
from bson import ObjectId

from actions import main, plot
from actions.enum_uniques import ID
from fuzzywuzzy import process

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, UserUtteranceReverted, ActionReverted
from rasa_sdk import Action, Tracker


with open('actions/responses.json', 'r') as file:
    data = json.load(file)

with open('actions/subjects.json', 'r') as file:
    subjects = json.load(file)

dict_vars = {'subject_idx': 0, 'topic_idx': 0, 'idx': 0}


def get_language_and_response(tracker: Tracker):

    user_language = tracker.get_slot('language')

    user_language = 'EN' if user_language is None else user_language

    response_query = data['language'][user_language]

    return user_language, response_query


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
        return "action_ask_subject"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_intent_of_latest_message() == "user_greet":
            return []

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_ask_subject']

        _, subject_dict = main.get_subjects()

        fixed_subjects = subject_dict[dict_vars['subject_idx']]

        buttons = [{'title': subjects["choices"][user_language][subject[0]],
                    'payload': '/inform_new{"subject":"'+subject[0]+'"}'} for subject in fixed_subjects]

        if dict_vars['subject_idx'] == 0:
            buttons.append(
                {"title": random.choice(message["next"]), "payload": '/next_option{"subject":"None"}'})
        else:
            buttons.append(
                {"title": random.choice(message["back"]), "payload": '/next_option{"subject":"BACK"}'})

        user_input = tracker.latest_message.get('text')

        subject_found, common_value = None, 70  # default values

        try:
            subject_list = subjects["choices"][user_language]["subject_list"]
            subject_found, common_value = process.extractOne(
                user_input, subject_list)
        except:
            pass

        if subject_found is not None and not user_input.startswith('/'):

            if common_value >= 70:
                print("common_value is: ", common_value)
                my_dict = subjects["choices"][user_language]
                dispatcher.utter_message(
                    f'{random.choice(message["found"])} {subject_found!r}')
                buttons = [{'title': random.choice(message["yes"]), 'payload': '/inform_new{"subject":"'+list(my_dict.keys())[list(my_dict.values()).index(subject_found)]+'"}'},  # add subject as entity
                           {'title': random.choice(message["no"]), 'payload': '/user_deny{"subject":"None"}'}]
                dispatcher.utter_message(
                    text=f'{random.choice(message["mean"])}', buttons=buttons, button_type="vertical")
                return []

        message = random.choice(message["available"])
        try:
            num_times = next(tracker.get_latest_entity_values('num_times'))
            print(f'{num_times = }')
            if num_times == 1:
                message = random.choice(message["choose"])
        except:
            pass

        dispatcher.utter_message(
            text=message, buttons=buttons, button_type="vertical")

        return []


class ActionGiveSuggestion(Action):

    def name(self) -> Text:
        return "action_give_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_give_suggestion']

        subs = main.get_subjects(collection_name='subjects')

        buttons = [{"title": sub, "payload": '/inform_new{"subject":"'+sub+'"}'}
                   for sub in subs]

        dispatcher.utter_message(
            text=random.choice(message), buttons=buttons)

        return []


class ActionTellTopics(Action):

    def name(self) -> Text:
        return "action_ask_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_ask_topic']

        subject = tracker.get_slot('subject')

        topic_length, topic_dict = main.get_topics(
            subject, user_language)  # List[List]

        if not topic_dict:
            dispatcher.utter_message(
                text=random.choice(message['not_available']))
            return [SlotSet('topic', 'NOT AVAILABLE'), SlotSet('question', 'NOT AVAILABLE')]

        topics = topic_dict[dict_vars['topic_idx']]

        buttons = [{'title': topic[0],
                    'payload': '/inform_new{"topic":"'+topic[1]+'"}'} for topic in topics]

        if dict_vars['topic_idx'] != 0:
            buttons.append(
                {"title": random.choice(message["back"]), "payload": '/next_option{"topic":"BACK"}'})

        if len(topics) >= ID.TOPIC_BUTTONS.value and topics != topic_dict[-1]:
            buttons.append(
                {"title": random.choice(message["next"]), "payload": '/next_option{"topic":"None"}'})

        response = random.choice(message['topic'])

        dispatcher.utter_message(
            text=response, buttons=buttons, button_type="vertical")

        return []


class ValidateSubmitWithTopicForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_subject_with_topic_form"

    def validate_subject(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        intent_value = tracker.get_intent_of_latest_message()

        if intent_value == "next_option":
            if slot_value == "BACK":
                dict_vars['subject_idx'] -= 1
                return {'subject': None}

            dict_vars['subject_idx'] += 1
            return {'subject': None}

        elif intent_value == "user_deny":
            return {'subject': None}

        dict_vars['subject_idx'] = 0

        sender_id = tracker.sender_id
        dict_vars[sender_id] = 0

        return {'subject': slot_value}

    def validate_topic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        intent_value = tracker.get_intent_of_latest_message()

        if intent_value == "next_option":
            if slot_value == "BACK":
                dict_vars['topic_idx'] -= 1
                return {'topic': None}

            dict_vars['topic_idx'] += 1
            return {'topic': None}

        elif intent_value == "user_deny":
            return {'topic': None}

        dict_vars['topic_idx'] = 0  # reset to start again

        if len(tracker.sender_id) < ID.ANDROID_UUID_LENGTH.value:
            return {'topic': slot_value, 'question': None}

        return {'topic': slot_value}


class ActionCleanEntity(Action):

    def name(self) -> Text:
        return "action_clean_entity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # reset dict before activation of form

        dict_vars['idx'] = 0
        dict_vars['subject_idx'] = 0

        return [SlotSet("subject", None), SlotSet("topic", None)]


class ActionCleanFeedbackformSlots(Action):

    def name(self) -> Text:
        return "action_clean_feedbackform_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("feedback", None), SlotSet("confirm_feedback", None)]


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

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_set_reminder']

        try:
            reminder_time = next(tracker.get_latest_entity_values('time'))
        except:
            pass

        if reminder_time == 'None' or reminder_time == None:
            dispatcher.utter_message(text=random.choice(message["time"]))
            return []

        time_object = dt.strptime(reminder_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        print(f'{time_object=}')
        dispatcher.utter_message(
            f'{random.choice(message["remind"])} {time_object.time()}.')

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

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_react_to_reminder']

        dispatcher.utter_message(text=random.choice(message))

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

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_forget_reminders']

        dispatcher.utter_message(text=random.choice(message))

        return [ReminderCancelled()]


class ActionGiveProgress(Action):

    def name(self) -> Text:
        return "action_give_progress"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_give_progress']

        dispatcher.utter_message(
            text=random.choice(message["message1"]))

        user_id = tracker.sender_id

        final_path, image_url = plot.image_url(user_id, current_time=dt.now())

        dispatcher.utter_message(
            text=f'{random.choice(message["message2"])}:', image=image_url)

        return []


class ActionGiveImprovement(Action):

    def name(self) -> Text:
        return "action_give_improvement"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)
        sender_id = tracker.sender_id

        message = response_query['action_give_improvement']

        with open('actions/improvements.json', 'r') as file:
            data = json.load(file)

        topic_dictionary = {'EN': data["low_scored_topics"]['english'],
                            'DE': data["low_scored_topics"]['german'],
                            'EL': data["low_scored_topics"]['greek'],
                            'ES': data["low_scored_topics"]['spanish']}

        if topic_dictionary[user_language].get(sender_id, None) == None:
            dispatcher.utter_message(text=random.choice(message["come_later"]))
            return []

        topics_to_improve = topic_dictionary[user_language][sender_id]

        buttons = [{'title': topic,
                    'payload': '/inform_new_topic{"topic":"'+topic_id+'"}'} for topic, topic_id in topics_to_improve.items()]

        limit = 5
        if len(buttons) >= limit:
            buttons = random.sample(buttons, limit)

        buttons.append({'title': random.choice(message["do_later"]),
                        'payload': "/user_done"})

        dispatcher.utter_message(text=random.choice(message["improve"]),
                                 buttons=buttons, button_type="vertical")

        return []


class ActionGiveApproach(Action):

    def name(self) -> Text:
        return "action_give_approach"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_give_approach']

        dispatcher.utter_message(text=random.choice(
            message))

        dispatcher.utter_message(
            "https://www.youtube.com/embed/73ZDMd3KmjU?cbrd=1")

        dispatcher.utter_message(
            "https://www.youtube.com/watch?v=ncUNgstfXcI&ab_channel=2MinuteClassroom")

        return []


class ActionGetFeedback(Action):

    def name(self) -> Text:
        return "action_get_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_get_feedback']

        dispatcher.utter_message(text=random.choice(message))

        return []


class ActionAskFeedback(Action):

    def name(self) -> Text:
        return "action_ask_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_ask_feedback']

        message_list = random.choice([message["choice1"], message["choice2"]])

        dispatcher.utter_message(text=random.choice(message_list))

        return []


class ActionAskConfirmFeedback(Action):

    def name(self) -> Text:
        return "action_ask_confirm_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_ask_confirm_feedback']

        if tracker.latest_message['text'] == 'No':
            return [ActionReverted(), SlotSet('feedback', None)]

        buttons = [{'title': random.choice(message["yes"]), 'payload': 'Yes'},
                   {'title': random.choice(message["no"]), 'payload': 'No'}]

        dispatcher.utter_message(
            text=random.choice(message["confirm"]),
            buttons=buttons, button_type="vertical")

        return []


# class ValidateQuestionsForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_feedback_form"

#     def validate_feedback(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict
#     ) -> Dict[Text, Any]:

#         user_language, response_query = get_language_and_response(tracker)

#         message = response_query['validate_feedback']

#         dispatcher.utter_message(
#             text=f'{random.choice(message)}{slot_value}')

#         return {'feedback': slot_value}

#     def validate_confirm_feedback(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict
#     ) -> Dict[Text, Any]:

#         if slot_value == 'Yes':
#             return {'confirm_feedback': 'Yes'}

#         return {'confirm_feedback': None}


class ActionShowFeatures(Action):

    def name(self) -> Text:
        return "action_show_features"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # user_id = tracker.sender_id

        user_id = str(tracker.sender_id)
        print(type(user_id))
        student_data = pd.read_excel('actions/student_db_new.xlsx')
        student_data = student_data.loc[:, ~
                                        student_data.columns.str.contains('^Unnamed')]  # removing "Unnamed" column
        student_data_list = student_data.values.tolist()
        user_exist = False
        for data in student_data_list:
            if str(user_id) == str(data[0]):
                user_exist = True

        if user_exist == False:
            student_data = pd.concat(
                [student_data, pd.DataFrame({'User': [user_id]})], ignore_index=True)
            student_data.fillna(0, inplace=True)
            # student_data.set_index('User', inplace=True)
            student_data.to_excel('actions/student_db_new.xlsx')

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_show_features']

        message_response = message["options"]

        message_response = message["start"] if tracker.get_intent_of_latest_message(
        ) == "start" else message_response

        if len(tracker.sender_id) > ID.TELEGRAM_UUID_LENGTH.value:
            buttons = [
                {'title': random.choice(
                    message["activity"]), 'payload': '/ask_for_suggestion'},
                {'title': random.choice(message["subject"]),
                 'payload': '/find_subject'},
                {'title': random.choice(message["question_types"]),
                 'payload': '/ask_question_types'},
                {'title': random.choice(message["improve"]),
                 'payload': '/ask_improvement'},
                {'title': random.choice(
                    message["bot"]), 'payload': '/bot_challenge'}
            ]

        else:
            buttons = [
                {'title': random.choice(
                    message["activity"]), 'payload': '/ask_for_suggestion'},
                {'title': random.choice(message["subject"]),
                 'payload': '/find_subject'},
                {'title': random.choice(message["question_types"]),
                 'payload': '/ask_question_types'},
                {'title': random.choice(message["progress"]),
                 'payload': '/ask_progress'},
                {'title': random.choice(message["approach"]),
                 'payload': '/ask_approach'},
                {'title': random.choice(message["reminder"]),
                 'payload': '/ask_remind_call{"time":"None"}'},
                {'title': random.choice(message["cancel_reminder"]),
                 'payload': '/ask_forget_reminders'},
                {'title': random.choice(message["feedback"]),
                 'payload': '/user_feedback'},
                {'title': random.choice(
                    message["bot"]), 'payload': '/bot_challenge'}
            ]

        dispatcher.utter_message(
            text=random.choice(
                message_response), buttons=buttons, button_type="vertical")

        return []


class ActionExplainQuestionTypes(Action):

    def name(self) -> Text:
        return "action_explain_question_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_explain_question_types']

        if len(tracker.sender_id) <= ID.ANDROID_UUID_LENGTH.value:
            buttons = [
                {'title': random.choice(
                    message["1"]), 'payload': '/ask_types{"type":"MCQ"}'},
                {'title': random.choice(message["2"]),
                 'payload': '/ask_types{"type":"True_False"}'}
            ]
        else:
            buttons = [
                {'title': random.choice(
                    message["1"]), 'payload': '/ask_types{"type":"MCQ"}'},
                {'title': random.choice(message["2"]),
                    'payload': '/ask_types{"type":"True_False"}'},
                {'title': random.choice(message["3"]),
                    'payload': '/ask_types{"type":"Matching_Pairs"}'},
                {'title': random.choice(message["4"]),
                    'payload': '/ask_types{"type":"Open_ended"}'}
            ]

        dispatcher.utter_message(
            text=random.choice(message["question"]),
            buttons=buttons, button_type="vertical")

        return []


class ActionExplainQuestionTypesDefinition(Action):

    def name(self) -> Text:
        return "action_explain_question_types_definition"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_explain_question_types_definition']

        entity = tracker.get_slot('type')

        explanation = {"MCQ": random.choice(message["MCQ"]),
                       "True_False": random.choice(message["True_False"]),
                       "Matching_Pairs": random.choice(message["Matching_Pairs"]),
                       "Open_ended": random.choice(message["Open_ended"])}

        if entity is not None:
            message = explanation[entity]
        else:
            message = random.choice(message["error"])
        dispatcher.utter_message(text=message)

        return []


class ActionContinue(Action):

    def name(self) -> Text:
        return "action_continue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_continue']

        question = tracker.get_slot('question')
        sender_id = tracker.sender_id

        try:
            if question == 'NOT AVAILABLE' or question.startswith('/inform_new'):
                pass
            else:
                dispatcher.utter_message(
                    text=random.choice(message["continue"]))
        except:
            pass

        try:
            score_1 = next(tracker.get_latest_entity_values('score1'))
            score_2 = next(tracker.get_latest_entity_values('score2'))
            topic_id = next(tracker.get_latest_entity_values('topic_id'))
            topic_completed = next(
                tracker.get_latest_entity_values('topic_completed'))

            with open('actions/improvements.json', 'r') as file:
                data = json.load(file)

            score_ratio = int(score_1)/int(score_2)

            if score_ratio <= 0.4:
                score_message = random.choice(message["<=0.4"])
            elif score_ratio <= 0.7:
                score_message = random.choice(message["<=0.7"])
            elif score_ratio < 1:
                score_message = random.choice(message["<1"])
            else:
                score_message = random.choice(message["1"])

            dispatcher.utter_message(text=score_message)

            topic_dictionary = {'EN': data["low_scored_topics"]['english'],
                                'DE': data["low_scored_topics"]['german'],
                                'EL': data["low_scored_topics"]['greek'],
                                'ES': data["low_scored_topics"]['spanish']}

            if topic_dictionary[user_language].get(sender_id, None) == None:
                topic_dictionary[user_language][sender_id] = {}

            if score_ratio <= 0.7:
                topic_dictionary[user_language][sender_id][topic_completed] = topic_id

            print(data)

            with open('actions/improvements.json', 'w') as file:
                json.dump(data, file)

        except Exception as e:
            print(e)

        buttons = [
            {'title': random.choice(message["yes"]),
                'payload': '/ask_for_suggestion{"num_times": 1}'},
            {'title': random.choice(message["no"]), 'payload': '/user_done'},
        ]

        dispatcher.utter_message(
            text=random.choice(message["one_more"]),
            buttons=buttons, button_type="vertical")

        return []


class ActionAskQuestion(Action):

    def name(self) -> Text:
        return "action_ask_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['validate_question']

        topic_id = tracker.get_slot('topic')

        # Base condition to check if Telegram user or Android user
        if len(tracker.sender_id) > ID.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(text=random.choice(
                response_query["good_time"]))
            return [SlotSet("question", "ANDROID APP")]

        question_count, questions_available = main.get_questions(topic_id)

        if question_count == 0:
            dispatcher.utter_message(
                text=random.choice(message["sorry"]))
            dispatcher.utter_message(text=random.choice(message["add_soon"]))
            return [SlotSet('question', 'NOT AVAILABLE')]

        sender_id = tracker.sender_id

        mcq_question = questions_available['mcq_question'][dict_vars[sender_id]].pop(
            0)
        mcq_choices = questions_available['mcq_choices'][dict_vars[sender_id]].pop(
            0)
        file = questions_available['file'][dict_vars[sender_id]].pop(0)

        buttons = [{"title": choice, "payload": f"option{idx+1}"}
                   for idx, choice in enumerate(mcq_choices)]

        # mcq_question = questions_available['mcq_question'][dict_vars['idx']].pop(
        #     0)
        # mcq_choices = questions_available['mcq_choices'][dict_vars['idx']].pop(
        #     0)
        # file = questions_available['file'][dict_vars['idx']].pop(0)

        # buttons = [{"title": choice, "payload": f"option{idx+1}"}
        #            for idx, choice in enumerate(mcq_choices)]

        buttons_new = []
        true_false_question_type = False

        message_2 = response_query['action_ask_question']

        for idx, choice in enumerate(mcq_choices):
            if choice == 'True' or choice == 'False':
                true_false_question_type = True
                buttons_new.append({"title": random.choice(
                    message_2["true"]), "payload": "true"})
                buttons_new.append({"title": random.choice(
                    message_2["false"]), "payload": "false"})

                break

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

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['validate_question']

        sender_id = tracker.sender_id

        if len(sender_id) > ID.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(random.choice(
                response_query["good_time"]))
            return {'question': 'ANDROID_APP'}

        topic_id = tracker.get_slot('topic')
        question_count, questions_available = main.get_questions(
            topic_id)

        if question_count == 0:
            dispatcher.utter_message(
                text=random.choice(message["sorry"]))
            dispatcher.utter_message(text=random.choice(message["add_soon"]))
            return [SlotSet('question', 'NOT AVAILABLE')]

        if slot_value.startswith('/inform_new'):
            return {'question': None}

        right_answer = questions_available['right_answer'][dict_vars[sender_id]].pop(
            0)
        pos_feedback = questions_available['feedback']['pos_feedback'][dict_vars[sender_id]].pop(
            0)
        neg_feedback = questions_available['feedback']['neg_feedback'][dict_vars[sender_id]].pop(
            0)

        if slot_value.startswith('/inform_new'):
            return {'question': None}
        elif slot_value.lower() == right_answer.lower():
            dispatcher.utter_message(text=pos_feedback)
        else:
            dispatcher.utter_message(text=neg_feedback)

        if dict_vars[sender_id] < question_count-1:
            dict_vars[sender_id] += 1
            return {'question': None}

        # dict_vars['idx'] = 0  # reset value of idx for the next interaction
        dict_vars.pop(sender_id)

        return {'question': 'FILLED'}
