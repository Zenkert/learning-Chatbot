from ctypes import Union
import os
import json
import requests
from dotenv import load_dotenv
from operator import itemgetter
from typing import Any, Text, Dict, List, Tuple, Generator

from actions.enum_uniques import Id


def chunks(list_to_chunk, length) -> Generator:
    '''
    yields chunks of list of length n
    '''

    # looping till length of the list_to_chunk
    for i in range(0, len(list_to_chunk), length):
        yield list_to_chunk[i:i + length]


def get_subjects() -> Tuple[List[Text], Tuple[Text, Text]]:
    '''
    returns list of complete subjects ['Biology', 'Math', ...]
    and chunked list of tuple of subject and subject_id [('Biology', '_id'), ('Math', '_id'), ...]
    '''

    load_dotenv()
    response = requests.get(os.getenv('ALL_SUBJECTS')).json()

    subject_list = [sub['subject'] for sub in response]

    subjects = [(sub['subject'], sub['_id']) for sub in response]

    subjects_chunk = list(chunks(subjects, Id.SUBJECT_BUTTONS.value))

    return subject_list, subjects_chunk


def get_topics_android(subject, language, **other_filters) -> Tuple[List[Text], Tuple[Text, Text]]:

    load_dotenv()
    subject_response = requests.get(os.getenv('ALL_SUBJECTS')).json()

    for sub in subject_response:
        if sub['subject'] == subject:
            subject_id = sub['_id']

    if other_filters:
        age = other_filters['age']  # user age
        grade = other_filters['grade']  # user grade
        private_key = other_filters['private_key']  # private key for material

    response = requests.get(os.getenv('ALL_TOPICS')).json()

    topic_list = [key['topic']
                  for key in response if key['subId'] == subject_id and key["language"] == language]

    topics = [(key['topic'], key['_id'])
              for key in response if key['subId'] == subject_id and key["language"] == language]

    topics_chunk = list(chunks(topics, Id.TOPIC_BUTTONS.value))

    return topic_list, topics_chunk


def get_topics_telegram(subject, language) -> Tuple[List[Text], Tuple[Text, Text]]:

    load_dotenv()
    subject_response = requests.get(os.getenv('ALL_SUBJECTS')).json()

    for sub in subject_response:
        if sub['subject'] == subject:
            subject_id = sub['_id']

    response = requests.get(os.getenv('ALL_TOPICS')).json()

    topic_list = [key['topic']
                  for key in response if key['subId'] == subject_id and key["language"] == language]

    topics = [(key['topic'], key['_id'])
              for key in response if key['subId'] == subject_id and key["language"] == language]

    topics_chunk = list(chunks(topics, Id.TOPIC_BUTTONS.value))

    return topic_list, topics_chunk


def get_questions(topic_id) -> Tuple[int, Dict[Text, Any], Dict[Text, Any]]:

    load_dotenv()
    response = requests.get(os.getenv('GET_QUIZ_BY_TOPIC')+topic_id).json()

    queried_data = {'mcq_question': [], 'mcq_choices': [], 'file': [], 'right_answer': [], 'feedback': {
        'pos_feedback': [], 'neg_feedback': []}}

    question_count = 0
    mcq_true_false_present = False

    for value in response:
        get_all_questions = value['allQuestions']
        all_questions = sorted(get_all_questions, key=itemgetter(
            'sequence'), reverse=False)  # sorted by sequence number

        for val in all_questions:
            if val['questionType'] == 'mcqs':
                question_count += 1
                mcq_true_false_present = True
                try:
                    queried_data['mcq_question'].append([val['mcqs']])
                    num_of_options = [val['option1'], val['option2']]
                    if val.get('option3', None) != None:
                        num_of_options.append(val['option3'])
                        if val.get('option4', None) != None:
                            num_of_options.append(val['option4'])
                    queried_data['mcq_choices'].append([num_of_options])
                    queried_data['file'].append([val.get('file', '')])
                    queried_data['right_answer'].append([val['answer']])
                    queried_data['feedback']['pos_feedback'].append(
                        [val['posFeedback']])
                    queried_data['feedback']['neg_feedback'].append(
                        [val['negFeedback']])
                except:
                    pass

            elif val['questionType'] == 'trueFalse':
                question_count += 1
                mcq_true_false_present = True
                try:
                    queried_data['mcq_question'].append(
                        [val['question']])
                    num_of_options = ['True', 'False']
                    queried_data['mcq_choices'].append(
                        [num_of_options])
                    queried_data['file'].append([val.get('file', '')])
                    queried_data['right_answer'].append(
                        [val['answer']])
                    queried_data['feedback']['pos_feedback'].append(
                        [val['posFeedback']])
                    queried_data['feedback']['neg_feedback'].append(
                        [val['negFeedback']])

                except:
                    pass

        question_intro = dict()
        for ques_type in all_questions:
            if mcq_true_false_present and ques_type['questionType'] == 'introduction':
                question_intro['introduction'] = ques_type['introduction']
                question_intro['link'] = ques_type['link'] if ques_type.get(
                    'link', None) != None else None
                question_intro['file'] = ques_type['file'] if ques_type.get(
                    'file', None) != None else None

                break

    return question_count, queried_data, question_intro


if __name__ == '__main__':
    # subject_list, subjects = get_subjects()
    # print(subject_list, subjects)

    # topic_list, topics_available = get_topics_telegram('Art and Design', 'DE')
    # print(topic_list, topics_available)

    question_count, queried_data, question_intro = get_questions(
        '6319d041c9b400710c0eced5')
    print(question_count, queried_data, question_intro)
