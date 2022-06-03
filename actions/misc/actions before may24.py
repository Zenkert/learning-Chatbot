
from random import choices
from matplotlib.pyplot import text
import pandas as pd
from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# import actions.main as main
# import actions.search as search

global i, j
i = 0 # to loop over list
j = 1 # subject number
num_of_questions = 4 # number of questions to ask the user per subject

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
            
            dj = pd.DataFrame(transcript, columns = ['Transcript'])
            dj.to_excel('user_transcript.xlsx')

            return []

class ActionUserData(Action):

    def name(self) -> Text:
        return "action_save_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            message = tracker.latest_message['text']
            print('message: ', message, 'message type: ', type(message))
            
            return []

class ActionTellJoke(Action):

    def name(self) -> Text:
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            f = search.joke()

            dispatcher.utter_message(text=f)

            return []

class ShowVideoAction(Action):
    def name(self) -> Text:
        return "action_give_show_video"

    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain:Dict) -> List[EventType]:
        
        # video_test = {"type":"video", "payload":{"title":"Trivia", "src":"https://www.youtube.com/embed/uG6U34se0yw"}}
        # # video_test = {"type":"video", "payload":{"title":"Link name", "src":"/home/sathish/mbot/unpacking.mp4"}}
        
        # dispatcher.utter_message(attachment = video_test)
        # message = 'This is the image'
        # src = 'https://upload.wikimedia.org/wikipedia/commons/e/eb/Ash_Tree_-_geograph.org.uk_-_590710.jpg'
        # dispatcher.utter_message(text=message, image = src)

        lll = next(tracker.get_latest_entity_values('scrape_query'), None)
        print('lll: ', lll)

        uuu = tracker.latest_message
        print('uuu: ', uuu)
        r = uuu['text']
        e = r.split()
        qtpi = e[-1]
        print('TEXT: ', e)
        print('TEXT[-1]: ', e[-1])

        ugpi = e[-2:]
        kk = ' '.join(ugpi)
        print('kk: ', kk)

        qqq = tracker.latest_message['entities']
        print('qqq: ', qqq)
        if qqq:
            xxx = qqq[0]['value']
            abc, uvw = search.imsearch(xxx)
            print('qqq, uvw: ', uvw)
        else:
            abc, uvw = search.imsearch(kk)
            print('kk, abc: ', abc)
            print('kk, uvw: ', uvw)
            if not uvw:
                abc, uvw = search.imsearch(qtpi)
                print('qtpi, uvw: ', uvw)

        if len(uvw) == 0:
            dispatcher.utter_message(text=abc)
            dispatcher.utter_message(text='can\'t find an image')
        else:
            dispatcher.utter_message(text=abc, image=uvw)

        return[]

class ActionAskSelectedSubject(Action):

    def name(self) -> Text:
        return "action_ask_selected_subject"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("-----------------------")

        quesz, subject_group1, subject_group2 = main.get_subjects() # call

        # print("Sub1: ", subject_group1)
        # print("Sub2: ", subject_group2)
        # print("-----------------------")

        # message = "Choose a Subject"
        # if j == 2: # if the user doesn't want to choose subjects from subject_group1
        #     button = [{'title': sub, 'payload': sub} for sub in subject_group2]
        # else:
        #     button = [{'title': sub, 'payload': sub} for sub in subject_group1]
        # dispatcher.utter_message(text = message, buttons = button)

        # data={ "title": "Options", "labels": [ "Option 1", "Option 2", "Option 3", "Option 4" ], "backgroundColor": [ "#36a2eb", "#ffcd56", "#ff6384", "#009688", "#c45850" ], "chartsData": [ 55, 10, 30, 15 ], "chartType": "pie", "displayLegend": "true" }

        # message={ "payload": "chart", "data": data }

        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",json_message=message)
        
        # dispatcher.utter_message(text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

        # optionss = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6"]

        # message = "Choose a Subject"
        # button = [{'title': opt, 'payload': opt} for opt in optionss]
        # dispatcher.utter_message(text = message, buttons = button)

        # dataa = [{'title': opt, 'payload': opt} for opt in optionss]
        # messagee={"payload":"quickReplies","data":dataa}
        # dispatcher.utter_message(text = "Choose a Subject", json_message=messagee)

        # data={ "title": "Options", "labels": [ "Option 1", "Option 2", "Option 3", "Option 4" ], "backgroundColor": [ "#36a2eb", "#ffcd56", "#ff6384", "#009688", "#c45850" ], "chartsData": [ 55, 10, 30, 15 ], "chartType": "pie", "displayLegend": "true" }

        # message={ "payload": "chart", "data": data }

        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",json_message=message)
        

        # message = "Choose a Subject"
        # button = [{'title': opt, 'payload': opt} for opt in optionss]
        # dispatcher.utter_message(text = message, buttons = button)

        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus posuere.")

        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.", image="https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1073&q=80")
        
        # msg = { "type": "video", "payload": { "title": "Title", "src": "https://www.youtube.com/embed/38sL6pADCog" } }

        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",attachment=msg)

        # data=[{"label":"option1","value":"/inform{'slot_name':'option1'}"},{"label":"option2","value":"/inform{'slot_name':'option2'}"},{"label":"option3","value":"/inform{'slot_name':'option3'}"}]

        # message={"payload":"dropDown","data":data}
        
        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",json_message=message)

        # data= [ { "title": "Option 1", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus posuere." }, { "title": "Option 2", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus posuere." }, { "title": "Option 3", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus posuere." }, { "title": "Option 4", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus posuere." } ]

        # message={ "payload": "collapsible", "data": data }

        # dispatcher.utter_message(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",json_message=message)

        # message = "Choose a Subject"
        # if j == 2: # if the user doesn't want to choose subjects from subject_group1
        #     button = [{'title': sub, 'payload': sub} for sub in subject_group2]
        # else:
        #     button = [{'title': sub, 'payload': sub} for sub in subject_group1]
        # dispatcher.utter_message(text = message, buttons = button)

        # print("-----------------------")


        # data = {
        #         "payload": 'cardsCarousel',
        #         "data": [
        #             {
        #                 "image": "https://images.unsplash.com/photo-1532153955177-f59af40d6472?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80",
        #                 "title": "Title 1",
        #                 "ratings": "4.5",
        #             },
        #             {
        #                 "image": "https://images.unsplash.com/photo-1586380951230-e6703d9f6833?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80",

        #                 "ratings": "4.0",
        #                 "title": "Title 2"
        #             },
        #             {
        #                 "image": "https://images.unsplash.com/photo-1576506542790-51244b486a6b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80",

        #                 "ratings": "3.0",
        #                 "title": "Title 3"
        #             }
        #         ]
        #     }
        # dispatcher.utter_message(json_message=data)

        data = {
                payload:"pdf_attachment",
                title: "PDF Title",
                url: "URL to PDF file"
            }
        dispatcher.utter_message(json_message=data)

        return []

class ActionAskSelectedXQuestions(Action):

    def name(self) -> Text:
        return "action_ask_selected_xquestions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        subject_chosen = tracker.get_slot('selected_subject')
        print("Subject: ", subject_chosen)
        
        questions_chosen, choice, _ = main.get_questions(subject_chosen) # call

        # data= [ { "title": "Sick Leave", "description": "Sick leave is time off from work that workers can use to stay home to address their health and safety needs without losing pay." }, { "title": "Earned Leave", "description": "Earned Leaves are the leaves which are earned in the previous year and enjoyed in the preceding years. " }, { "title": "Casual Leave", "description": "Casual Leave are granted for certain unforeseen situation or were you are require to go for one or two days leaves to attend to personal matters and not for vacation." }, { "title": "Flexi Leave", "description": "Flexi leave is an optional leave which one can apply directly in system at lease a week before." } ]

        # message={ "payload": "collapsible", "data": data }

        # dispatcher.utter_message(text="You can apply for below leaves",json_message=message)


        message = questions_chosen[i]
        button = [{'title': cho, 'payload': cho} for cho in choice[i]]
        dispatcher.utter_message(text = message, buttons = button)
        return []

class ValidateSelectSubjectForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_select_subject_form"

    def validate_selected_subject(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        global j
        print('-----validation selected subject-----')
        if slot_value == "Other options":
            j += 1
            return {'selected_subject': None}
        else:
            j = 1 # reset j globally
            return {'selected_subject': slot_value}

    def validate_selected_xquestions(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        global i
        print('-----validation selected questions-----')
        subject_chosen = tracker.get_slot('selected_subject')
        _, _, correct_answer = main.get_questions(subject_chosen) # call
        
        if slot_value == correct_answer[i]:
            dispatcher.utter_message(text = 'You got it right!')
        else:
            dispatcher.utter_message(text = 'Oh, it\'s wrong!')
            say_correct_answer = f'The correct answer is {correct_answer[i]}'
            dispatcher.utter_message(text = say_correct_answer)
            
        if i < num_of_questions:
            i += 1
            print('i ==> ', i)
            return {'selected_xquestions': None}
        i = 0 # reset value of i to loop again
        return {'selected_xquestions': slot_value}

class ActionAskSelectedSubjectGerman(Action):

    def name(self) -> Text:
        return "action_ask_selected_subject_german"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("-----------------------")

        quesz, subject_group1, subject_group2 = main.get_subjects() # call

        # print("Sub1: ", subject_group1)
        # print("Sub2: ", subject_group2)
        # print("-----------------------")


        message = "Wählen Sie ein Thema"
        if j == 2: # if the user doesn't want to choose subjects from subject_group1
            button = [{'title': sub, 'payload': sub} for sub in subject_group2]
        else:
            button = [{'title': sub, 'payload': sub} for sub in subject_group1]
        dispatcher.utter_message(text = message, buttons = button)
        print("-----------------------")

        return []

class ActionAskSelectedXQuestionsGerman(Action):

    def name(self) -> Text:
        return "action_ask_selected_xquestions_german"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        subject_chosen = tracker.get_slot('selected_subject_german')
        print("Subject: ", subject_chosen)
        
        questions_chosen, choice, _ = main.get_questions(subject_chosen) # call

        message = questions_chosen[i]
        button = [{'title': cho, 'payload': cho} for cho in choice[i]]
        dispatcher.utter_message(text = message, buttons = button)
        return []

class ValidateSelectSubjectFormGerman(FormValidationAction):
    def name(self) -> Text:
        return "validate_select_subject_form_german"

    def validate_selected_subject_german(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        global j
        print('-----validation selected subject-----')
        if slot_value == "Other options":
            j += 1
            return {'selected_subject_german': None}
        else:
            j = 1 # reset j globally
            return {'selected_subject_german': slot_value}

    def validate_selected_xquestions_german(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        global i
        print('-----validation selected questions-----')
        subject_chosen = tracker.get_slot('selected_subject_german')
        _, _, correct_answer = main.get_questions(subject_chosen) # call
        
        if slot_value == correct_answer[i]:
            dispatcher.utter_message(text = 'richtig gemacht!')
        else:
            dispatcher.utter_message(text = 'stimmt nicht!')
            say_correct_answer = f'Die richtige Antwort lautet {correct_answer[i]}'
            dispatcher.utter_message(text = say_correct_answer)
            
        if i < num_of_questions:
            i += 1
            print('i ==> ', i)
            return {'selected_xquestions_german': None}
        i = 0 # reset value of i to loop again
        return {'selected_xquestions_german': slot_value}

class ActionAskSelectedSubjectGreek(Action):

    def name(self) -> Text:
        return "action_ask_selected_subject_greek"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("-----------------------")

        quesz, subject_group1, subject_group2 = main.get_subjects() # call

        # print("Sub1: ", subject_group1)
        # print("Sub2: ", subject_group2)
        # print("-----------------------")


        message = "παρακαλώ επιλέξτε ένα θέμα"
        if j == 2: # if the user doesn't want to choose subjects from subject_group1
            button = [{'title': sub, 'payload': sub} for sub in subject_group2]
        else:
            button = [{'title': sub, 'payload': sub} for sub in subject_group1]
        dispatcher.utter_message(text = message, buttons = button)
        print("-----------------------")

        return []

class ActionAskSelectedXQuestionsGreek(Action):

    def name(self) -> Text:
        return "action_ask_selected_xquestions_greek"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        subject_chosen = tracker.get_slot('selected_subject_greek')
        print("Subject: ", subject_chosen)
        
        questions_chosen, choice, _ = main.get_questions(subject_chosen) # call

        message = questions_chosen[i]
        button = [{'title': cho, 'payload': cho} for cho in choice[i]]
        dispatcher.utter_message(text = message, buttons = button)
        return []

class ValidateSelectSubjectFormGreek(FormValidationAction):
    def name(self) -> Text:
        return "validate_select_subject_form_greek"

    def validate_selected_subject_greek(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        global j
        print('-----validation selected subject-----')
        if slot_value == "Other options":
            j += 1
            return {'selected_subject_greek': None}
        else:
            j = 1 # reset j globally
            return {'selected_subject_greek': slot_value}

    def validate_selected_xquestions_greek(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        global i
        print('-----validation selected questions-----')
        subject_chosen = tracker.get_slot('selected_subject_greek')
        _, _, correct_answer = main.get_questions(subject_chosen) # call
        
        if slot_value == correct_answer[i]:
            dispatcher.utter_message(text = 'είναι σωστό!')
        else:
            dispatcher.utter_message(text = 'είναι λάθος!')
            say_correct_answer = f'Η σωστή απάντηση είναι {correct_answer[i]}'
            dispatcher.utter_message(text = say_correct_answer)
            
        if i < num_of_questions:
            i += 1
            print('i ==> ', i)
            return {'selected_xquestions_greek': None}
        i = 0 # reset value of i to loop again
        return {'selected_xquestions_greek': slot_value}

    
