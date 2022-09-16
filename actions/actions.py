import os
import json
import random
import pandas as pd
from dotenv import load_dotenv
from fuzzywuzzy import process
from datetime import datetime as dt
from typing import Any, Text, Dict, List, Tuple

from actions import plot
from actions import query_db
from actions.enum_uniques import Id

from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import SlotSet, EventType, AllSlotsReset, FollowupAction
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, ActionReverted


with open('actions/responses.json', 'r') as file:
    data = json.load(file)

with open('actions/subjects.json', 'r') as file:
    subjects = json.load(file)

# to keep track of unique sender_id for the session {'sender_id': interaction_count}
user_interaction = dict()


def get_language_and_response(tracker: Tracker) -> Tuple[Text, Dict[Text, Text]]:
    '''
    returns the language in which the user is conversing and the corresponding responses in that language.
    '''

    user_language = tracker.get_slot('language')

    # set a default language 'EN' if there is no user language present
    user_language = 'EN' if user_language is None else user_language

    response_query = data['language'][user_language]

    return user_language, response_query


class ActionSetLanguage(Action):

    def name(self) -> Text:
        return "action_set_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        raise NotImplementedError


class ActionTellSubjects(Action):

    def name(self) -> Text:
        return "action_ask_subject"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_intent_of_latest_message() == "user_greet":
            return []

        sender_id = tracker.sender_id

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_ask_subject']

        _, subject_dict = query_db.get_subjects()

        user_interaction[sender_id] = 0 if user_interaction.get(
            sender_id, None) == None else user_interaction[sender_id]

        fixed_subjects = subject_dict[user_interaction[sender_id]]

        # subject[0]:str is the name of the subject
        # subjects["choices"][user_language][subject[0]]:str is the translated name of the respective subject[0]
        buttons = [{'title': subjects["choices"][user_language][subject[0]],
                    'payload': '/inform_new{"subject":"'+subject[0]+'"}'} for subject in fixed_subjects]

        if user_interaction[sender_id] == 0:
            buttons.append(
                {"title": random.choice(message["next"]),
                 "payload": '/next_option{"subject":"None"}'})
        else:
            buttons.append(
                {"title": random.choice(message["back"]),
                 "payload": '/next_option{"subject":"BACK"}'})

        if len(sender_id) < Id.TELEGRAM_UUID_LENGTH.value:
            buttons.append(
                {"title": 'STOP',
                 "payload": '/user_stop{"subject":"STOP"}'})

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
                my_dict = subjects["choices"][user_language]
                dispatcher.utter_message(
                    f'{random.choice(message["found"])} {subject_found!r}')

                buttons = [{'title': random.choice(message["yes"]),
                            'payload': '/inform_new{"subject":"'+list(my_dict.keys())[list(my_dict.values()).index(subject_found)]+'"}'},  # add subject as entity
                           {'title': random.choice(message["no"]),
                           'payload': '/user_deny{"subject":"None"}'}]

                dispatcher.utter_message(
                    text=f'{random.choice(message["mean"])}',
                    buttons=buttons,
                    button_type="vertical")
                return []

        response = random.choice(message["available"]) if user_interaction[sender_id] == 0 else random.choice(
            message["available_2"])

        try:
            num_times = next(tracker.get_latest_entity_values('num_times'))
            if int(num_times) == 1:
                response = random.choice(message["choose"])
        except:
            pass

        dispatcher.utter_message(
            text=response, buttons=buttons, button_type="vertical")

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
        sender_id = tracker.sender_id

        # 50-50 chance of uttering the subject selection to the user
        if random.choice([True, False]):
            dispatcher.utter_message(text=random.choice(
                message['sub_choice'][subject]))

        material_language = tracker.get_slot('material_language')
        user_age = tracker.get_slot('age')
        user_grade = tracker.get_slot('grade')

        user_interaction[sender_id] = 0 if user_interaction.get(
            sender_id, None) == None else user_interaction[sender_id]

        if len(sender_id) > Id.TELEGRAM_UUID_LENGTH.value:
            material_language_from_enum = Id[material_language].value
            topic_length, topic_dict = query_db.get_topics_android(
                subject, material_language_from_enum, age=user_age, grade=user_grade)
        else:
            language_from_enum = Id[user_language].value
            topic_length, topic_dict = query_db.get_topics_telegram(
                subject, language_from_enum)  # List[List]

        if not topic_dict:
            dispatcher.utter_message(
                text=random.choice(message['not_available']))
            return [SlotSet('topic', 'NOT AVAILABLE'), SlotSet('question', 'NOT AVAILABLE')]

        topics = topic_dict[user_interaction[sender_id]]

        buttons = [{'title': topic[0],
                    'payload': '/inform_new{"topic":"'+topic[1]+'"}'} for topic in topics]

        if user_interaction[sender_id] != 0:
            buttons.append(
                {"title": random.choice(message["back"]),
                 "payload": '/next_option{"topic":"BACK"}'})

        if len(topics) >= Id.TOPIC_BUTTONS.value and topics != topic_dict[-1]:
            buttons.append(
                {"title": random.choice(message["next"]),
                 "payload": '/next_option{"topic":"None"}'})

        if len(sender_id) < Id.TELEGRAM_UUID_LENGTH.value:
            buttons.append(
                {"title": 'STOP',
                 "payload": '/user_stop{"subject":"topic"}'})

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

        user_intent = tracker.get_intent_of_latest_message()
        sender_id = tracker.sender_id

        def next_option() -> Dict[Text, Any]:
            if slot_value == "BACK":
                user_interaction[sender_id] -= 1
                return {'subject': None}

            user_interaction[sender_id] += 1
            return {'subject': None}

        def user_deny() -> Dict[Text, Any]:
            return {'subject': None}

        def user_stop() -> Dict[Text, Any]:
            return {'subject': 'STOP', 'topic': 'STOP', 'question': 'STOP'}

        functions_available = {'next_option': next_option,
                               'user_deny': user_deny, 'user_stop': user_stop}

        if user_intent in functions_available:
            return functions_available[user_intent]()

        # user_interaction[sender_id] needed only for respective session
        user_interaction.pop(sender_id)

        return {'subject': slot_value}

    def validate_topic(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:

        user_intent = tracker.get_intent_of_latest_message()
        sender_id = tracker.sender_id

        def next_option() -> Dict[Text, Any]:
            if slot_value == "BACK":
                user_interaction[sender_id] -= 1
                return {'topic': None}

            user_interaction[sender_id] += 1
            return {'topic': None}

        def user_deny() -> Dict[Text, Any]:
            return {'topic': None}

        def user_stop() -> Dict[Text, Any]:
            return {'topic': 'STOP', 'question': 'STOP'}

        functions_available = {'next_option': next_option,
                               'user_deny': user_deny, 'user_stop': user_stop}

        if user_intent in functions_available:
            return functions_available[user_intent]()

        # user_interaction[sender_id] needed only for respective session
        user_interaction.pop(sender_id)

        if len(sender_id) < Id.ANDROID_UUID_LENGTH.value:
            return {'topic': slot_value, 'question': None}

        return {'topic': slot_value}


class ActionCleanEntity(Action):

    def name(self) -> Text:
        return "action_clean_entity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # clean subject and topic slot before activation of form

        return [SlotSet("subject", None), SlotSet("topic", None)]


class ActionCleanFeedbackformSlots(Action):

    def name(self) -> Text:
        return "action_clean_feedbackform_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # clean feedback and confirm_feedback slot before activation of form

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

        # clean time slot to use the slot for futher interactions

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

        # ReminderCancelled event to cancel the reminder
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

        final_path, image_url = plot.image_url(
            user_id, user_language, current_time=dt.now())

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

        if topic_dictionary[user_language].get(sender_id, None) != None:
            if not topic_dictionary[user_language][sender_id]:
                dispatcher.utter_message(
                    text=random.choice(message["come_later"]))
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

        # default videos to show in Telegram bot
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

        if len(tracker.sender_id) > Id.TELEGRAM_UUID_LENGTH.value:
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

            with open('actions/improvements.json', 'r') as file:
                data = json.load(file)

            topic_dictionary = {'EN': data["low_scored_topics"]['english'],
                                'DE': data["low_scored_topics"]['german'],
                                'EL': data["low_scored_topics"]['greek'],
                                'ES': data["low_scored_topics"]['spanish']}

            if topic_dictionary[user_language].get(sender_id, None) == None:
                topic_dictionary[user_language][sender_id] = {}

            if score_ratio <= Id.IMPROVEMENT_SUGGESTION_RATIO.value:
                topic_dictionary[user_language][sender_id][topic_completed] = topic_id

            if score_ratio > Id.IMPROVEMENT_SUGGESTION_RATIO.value:
                # remove topic from dictionary if user gets good score
                _ = topic_dictionary[user_language][sender_id].pop(
                    topic_completed, None)

            with open('actions/improvements.json', 'w') as file:
                json.dump(data, file)

        except Exception as e:
            print(e)

        buttons = [
            {'title': random.choice(message["yes"]),
                'payload': '/ask_for_suggestion{"num_times": "1"}'},
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

        load_dotenv()

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['validate_question']

        topic_id = tracker.get_slot('topic')
        sender_id = tracker.sender_id

        user_interaction[sender_id] = -1 if user_interaction.get(
            sender_id, None) == None else user_interaction[sender_id]

        user_interaction['intro'+sender_id] = -1 if user_interaction.get(
            'intro'+sender_id, None) == None else user_interaction['intro'+sender_id]

        # Base condition to check if Telegram user or Android user
        if len(sender_id) > Id.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(text=random.choice(
                response_query["good_time"]))
            return [SlotSet("question", "ANDROID APP")]

        unique_questions = query_db.get_questions(sender_id, topic_id)
        question_count = unique_questions[sender_id]['question_count']
        questions_available = unique_questions[sender_id]['queried_data']
        question_intro = unique_questions[sender_id]['question_intro']
        intro_count = unique_questions[sender_id]['introduction_count']

        if question_count == 0:
            dispatcher.utter_message(
                text=random.choice(message["sorry"]))
            dispatcher.utter_message(text=random.choice(message["link_below"]))
            dispatcher.utter_message(
                attachment='https://play.google.com/store/apps/details?id=com.moodle.moodlemobile')

            return [SlotSet('question', 'NOT AVAILABLE')]

        mcq_question = questions_available['mcq_question'][
            user_interaction[sender_id]].pop(0)
        mcq_choices = questions_available['mcq_choices'][
            user_interaction[sender_id]].pop(0)
        file = questions_available['file'][
            user_interaction[sender_id]].pop(0)
        sequence_types = questions_available['sequence'][
            user_interaction[sender_id]].pop(0)
        sequence_intro = question_intro['sequence'][
            user_interaction['intro'+sender_id]].pop(
            0) if abs(user_interaction['intro'+sender_id]) <= intro_count else 99  # max value

        # option{idx+1} gives option1, option2,... as the payload for the respective choices
        buttons = [{"title": choice, "payload": f"option{idx+1}"}
                   for idx, choice in enumerate(mcq_choices)]

        buttons_true_false = []
        true_false_question_type = False
        file_present = True if file != '' else False

        message_2 = response_query['action_ask_question']

        for idx, choice in enumerate(mcq_choices):
            if choice == 'True' or choice == 'False':
                true_false_question_type = True

                buttons_true_false.append({
                    "title": random.choice(message_2["true"]),
                    "payload": "true"})
                buttons_true_false.append({
                    "title": random.choice(message_2["false"]),
                    "payload": "false"})

                break

        if abs(user_interaction['intro'+sender_id]) <= intro_count:
            introduction = question_intro['introduction'][
                user_interaction['intro'+sender_id]].pop(0)
            introduction_file = question_intro['file'][
                user_interaction['intro'+sender_id]].pop(0)
            introduction_link = question_intro['link'][
                user_interaction['intro'+sender_id]].pop(0)

            if sequence_intro < sequence_types:
                user_interaction['intro'+sender_id] -= 1
                dispatcher.utter_message(text=introduction)

                if introduction_link != None and introduction_link != '':
                    dispatcher.utter_message(text=introduction_link)

                if introduction_file != None and introduction_file != '':
                    dispatcher.utter_message(
                        text=f'introduction_file is {introduction_file}')
                    file_split = introduction_file.split('5000')
                    link_secure = os.getenv('SECURE_HTTPS')
                    url_secure = link_secure+file_split[1]
                    dispatcher.utter_message(image=url_secure)

        def split_file_and_secure() -> Text:
            '''
            returns https link for the file(image)
            '''

            # Link from database is http which is not secure
            # converting from http to https with AWS API Gateway
            secure_link = os.getenv('SECURE_HTTPS')
            split_file = file.split('5000')

            return secure_link+split_file[1]

        if true_false_question_type:
            if not file_present:
                dispatcher.utter_message(
                    text=mcq_question,
                    buttons=buttons_true_false,
                    button_type="vertical")
                return []

            secure_file_url = split_file_and_secure()

            dispatcher.utter_message(
                text=mcq_question,
                image=secure_file_url,
                buttons=buttons_true_false,
                button_type="vertical")

        else:
            if not file_present:
                dispatcher.utter_message(
                    text=mcq_question,
                    buttons=buttons,
                    button_type="vertical")
                return []

            secure_file_url = split_file_and_secure()

            dispatcher.utter_message(
                text=mcq_question,
                image=secure_file_url,
                buttons=buttons,
                button_type="vertical")

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

        intent_value = tracker.get_intent_of_latest_message()

        # exit form if user doesn't want to continue
        if intent_value == "user_stop":
            _, response_query = get_language_and_response(tracker)

            message = response_query['action_done']

            dispatcher.utter_message(
                text=random.choice(message["done"]))

            return {'question': 'STOP'}

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['validate_question']

        sender_id = tracker.sender_id

        if len(sender_id) > Id.TELEGRAM_UUID_LENGTH.value:
            dispatcher.utter_message(random.choice(
                response_query["good_time"]))
            return {'question': 'ANDROID_APP'}

        topic_id = tracker.get_slot('topic')

        unique_questions = query_db.get_questions(sender_id, topic_id)
        question_count = unique_questions[sender_id]['question_count']
        questions_available = unique_questions[sender_id]['queried_data']

        if slot_value.startswith('/inform_new'):
            return {'question': None}

        right_answer = questions_available['right_answer'][
            user_interaction[sender_id]].pop(0)
        pos_feedback = questions_available['feedback'][
            'pos_feedback'][user_interaction[sender_id]].pop(0)
        neg_feedback = questions_available['feedback'][
            'neg_feedback'][user_interaction[sender_id]].pop(0)

        if slot_value.startswith('/inform_new'):
            return {'question': None}
        elif slot_value.lower() == right_answer.lower():
            dispatcher.utter_message(text=pos_feedback)
        else:
            dispatcher.utter_message(text=neg_feedback)

        if abs(user_interaction[sender_id]) < question_count:
            user_interaction[sender_id] -= 1
            return {'question': None}

        # user_interaction[sender_id] needed only for respective session
        user_interaction.pop(sender_id)
        user_interaction.pop('intro'+sender_id)

        return {'question': 'FILLED'}


class ActionExplainQuestionTypes(Action):

    def name(self) -> Text:
        return "action_explain_question_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_language, response_query = get_language_and_response(tracker)

        message = response_query['action_explain_question_types']

        if len(tracker.sender_id) <= Id.ANDROID_UUID_LENGTH.value:
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
