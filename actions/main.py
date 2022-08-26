from pydoc_data.topics import topics
from urllib import response
import requests

from enum import Enum

# from dataclasses import dataclass, field
# import collections


class ID(Enum):
    ANDROID_UUID_LENGTH = 16
    TELEGRAM_UUID_LENGTH = 10


def get_subjects():
    response = requests.get(
        'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/subject/get').json()

    subject_list = [s['subject'] for s in response]

    subjects = {s['subject']: s['_id'] for s in response}

    return subject_list, subjects


def get_topics(subj):
    subject_response = requests.get(
        'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/subject/get').json()

    for s in subject_response:
        if s['subject'] == subj:
            subject_id = s['_id']

    response = requests.get(
        'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/topic').json()

    topic_list = [s['topic']
                  for s in response if s['subId'] == subject_id]

    topics = {s['topic']: s['_id']
              for s in response if s['subId'] == subject_id}

    return topic_list, topics


def get_questions(topic_id):

    response = requests.get(
        f'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/topic/getByTopic/{topic_id}').json()

    queried_data = {'mcq_question': [], 'mcq_choices': [],  'right_answer': [], 'feedback': {
        'pos_feedback': [], 'neg_feedback': []}}

    # queried_data = {'mcq': {'mcq_question': [], 'mcq_choices': [],  'right_answer': [], 'feedback': {
    #     'pos_feedback': [], 'neg_feedback': []}},
    #     'truefalse': {'true_false': [], 'choices': [],  'right_answer': [], 'feedback': {
    #         'pos_feedback': [], 'neg_feedback': []}}}
    question_count = 0

    for value in response:
        all_questions = value['allQuestions']
        # print(type(zz), zz)
        for val in all_questions:
            if val['questionType'] == 'mcqs':
                question_count += 1
                try:
                    queried_data['mcq_question'].append(val['mcqs'])
                    num_of_options = [val['option1'], val['option2']]
                    if val.get('option3', None) != None:
                        num_of_options.append(val['option3'])
                        if val.get('option4', None) != None:
                            num_of_options.append(val['option4'])
                    queried_data['mcq_choices'].append(num_of_options)
                    queried_data['right_answer'].append(val['answer'])
                    queried_data['feedback']['pos_feedback'].append(
                        val['posFeedback'])
                    queried_data['feedback']['neg_feedback'].append(
                        val['negFeedback'])
                except:
                    print('----- ERROR -----')
            elif val['questionType'] == 'trueFalse':
                question_count += 1
                try:
                    queried_data['mcq_question'].append(
                        val['question'])
                    num_of_options = ['True', 'False']
                    queried_data['mcq_choices'].append(
                        num_of_options)
                    queried_data['right_answer'].append(
                        val['answer'])
                    queried_data['feedback']['pos_feedback'].append(
                        val['posFeedback'])
                    queried_data['feedback']['neg_feedback'].append(
                        val['negFeedback'])
                    # queried_data['truefalse']['true_false'].append(
                    #     val['question'])
                    # num_of_options = ['True', 'False']
                    # queried_data['truefalse']['choices'].append(
                    #     num_of_options)
                    # queried_data['truefalse']['right_answer'].append(
                    #     val['answer'])
                    # queried_data['truefalse']['feedback']['pos_feedback'].append(
                    #     val['posFeedback'])
                    # queried_data['truefalse']['feedback']['neg_feedback'].append(
                    #     val['negFeedback'])
                except:
                    print('----- ERROR -----')

    return question_count, queried_data


if __name__ == '__main__':
    # subject_list, subjects = get_subjects()
    # print(subject_list, subjects)

    # topic_list, topics_available = get_topics('Humanities')
    # print(topic_list, topics_available)

    question_count, queried_data = get_questions(
        '62f22b06c992eabdda6fbd93')
    print(question_count, queried_data)


# All mcqs: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/mcqs

# All topics: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/topic

# All grades: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/grade/get

# All age groups: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/age/get

# All subjects: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/subject/get

# All true false: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/true_false

# Get quiz by topic ID: http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/topic/getByTopic/62f22b06c992eabdda6fbd93
