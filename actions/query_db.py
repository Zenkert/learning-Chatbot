import os
import json
import requests
from dotenv import load_dotenv
from functools import lru_cache
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


def get_all_topics() -> Tuple[Text, Text]:
    '''
    returns all the topics present in the database [('Cultural Layers', '_id'), ('Painting & Painters', '_id'), ...]
    irrespective of the subject
    '''

    load_dotenv()
    subject_response = requests.get(os.getenv('ALL_TOPICS')).json()

    topic_list = [(subjects["topic"], subjects["_id"])
                  for subjects in subject_response]

    return topic_list


def get_topics_android(subject, language, **other_filters) -> Tuple[List[Text], Tuple[Text, Text]]:
    '''
    returns list of topics associated with the subject ['Cultural Layers', 'Painting & Painters', ...]
    and chunked list of tuple of topic and topic_id [('Cultural Layers', '_id'), ('Painting & Painters', '_id'), ...]
    '''

    load_dotenv()

    subject_response = requests.get(os.getenv('ALL_SUBJECTS')).json()

    for sub in subject_response:
        if sub['subject'] == subject:
            subject_id = sub['_id']

    with open("actions/age_and_grade.json", 'r') as file:
        age_and_grade = json.load(file)

    # age_group = {age_group_in_android_app:age_group_in_database,...}
    age_group = age_and_grade["age_group"]
    grade_list = age_and_grade["grade_list"]

    # user age with default age of "6-7"
    age = other_filters.get('age', None)
    age = age if age in age_group else "6-7"

    # user grade with default grade 0f "ELEMENTARY SCHOOL Grade 1"
    grade = other_filters.get('grade', None)
    grade = grade if grade in grade_list else "ELEMENTARY SCHOOL Grade 1"

    private_key = other_filters.get(
        'private_key', None)  # private key for material

    response = requests.get(os.getenv('ALL_TOPICS')).json()

    # without age and grade filter for testing
    topic_list = [key['topic']
                  for key in response if key['subId'] == subject_id and key["language"] == language]

    topics = [(key['topic'], key['_id'])
              for key in response if key['subId'] == subject_id and key["language"] == language]

    # with age and grade filter for production
    # topic_list = [key['topic']
    #               for key in response if key['subId'] == subject_id and key["language"] == language
    #               and key['ageGroup'] == age_group[age] and key['grade'] == grade]

    # topics = [(key['topic'], key['_id'])
    #           for key in response if key['subId'] == subject_id and key["language"] == language
    #           and key['ageGroup'] == age_group[age] and key['grade'] == grade]

    topics_chunk = list(chunks(topics, Id.TOPIC_BUTTONS.value))

    return topic_list, topics_chunk


def get_topics_telegram(subject, language) -> Tuple[List[Text], Tuple[Text, Text]]:
    '''
    returns list of topics associated with the subject ['Cultural Layers', 'Painting & Painters', ...]
    and chunked list of tuple of topic and topic_id [('Cultural Layers', '_id'), ('Painting & Painters', '_id'), ...]
    '''

    load_dotenv()
    subject_response = requests.get(os.getenv('ALL_SUBJECTS')).json()

    for sub in subject_response:
        if sub['subject'] == subject:
            subject_id = sub['_id']

    response = requests.get(os.getenv('ALL_TOPICS')).json()

    # filtered by subject_id, user_language, non-private material
    topic_list = [key['topic']
                  for key in response if key['subId'] == subject_id and key["language"] == language
                  and key['access'] == False]

    # filtered by subject_id, user_language, non-private material
    topics = [(key['topic'], key['_id'])
              for key in response if key['subId'] == subject_id and key["language"] == language
              and key['access'] == False]

    topics_chunk = list(chunks(topics, Id.TOPIC_BUTTONS.value))

    return topic_list, topics_chunk


@lru_cache(maxsize=10)
def get_questions(sender_id, topic_id) -> Dict[Text, Any]:
    '''
    returns unique_questions for the sender with unique session
    '''

    load_dotenv()

    response = requests.get(os.getenv('GET_QUIZ_BY_TOPIC')+topic_id).json()

    queried_data = {
        'mcq_question': [],
        'mcq_choices': [],
        'file': [],
        'right_answer': [],
        'feedback':
        {
            'pos_feedback': [],
            'neg_feedback': []
        },
        'sequence': []
    }

    question_intro = {
        'introduction': [],
        'link': [],
        'file': [],
        'sequence': []
    }

    question_count, introduction_count = 0, 0

    # questions available for unique user {sender_id:questions}
    unique_questions = dict()

    for value in response:
        get_all_questions = value['allQuestions']
        # sorted by sequence number
        # reverse is true to check if introduction is only associated with mcqs & true_false
        all_questions = sorted(get_all_questions, key=itemgetter(
            'sequence'), reverse=True)

    mcq_true_false_present = False

    for val in all_questions:
        question_type = val['questionType']

        mcq_true_false_present = False if question_type in [
            'matchPairs', 'openEnded'] else mcq_true_false_present

        # trueFalse is written in camelCase to match the value from database
        # please adhere to snake_case in Python ;)
        types_supported_in_telegram = {
            "mcqs": mcq_type,
            "trueFalse": true_false_type
        }

        additional_types = {"introduction": introduction_type}

        if question_type in types_supported_in_telegram:
            question_count += 1
            mcq_true_false_present = True
            types_supported_in_telegram[question_type](val, queried_data)

        elif question_type in additional_types and mcq_true_false_present:
            introduction_count += 1
            additional_types[question_type](val, question_intro)

    unique_questions[sender_id] = {
        'question_count': question_count,
        'queried_data': queried_data,
        'question_intro': question_intro,
        'introduction_count': introduction_count
    }

    return unique_questions


def introduction_type(val, question_intro) -> Dict[Text, List[Any]]:

    question_intro['introduction'].append([val['introduction']])
    question_intro['sequence'].append([val['sequence']])
    question_intro['link'].append([val['link']]) if val.get(
        'link', None) != None else None
    question_intro['file'].append([val['file']]) if val.get(
        'file', None) != None else None

    return question_intro


def mcq_type(val, queried_data) -> Dict[Text, List[Any]]:

    queried_data['mcq_question'].append([val['mcqs']])
    num_of_options = [
        val['option1'],
        val['option2'],
        val['option3'],
        val['option4']
    ]
    queried_data['mcq_choices'].append([num_of_options])
    queried_data['file'].append([val.get('file', '')])
    queried_data['right_answer'].append([val['answer']])
    queried_data['feedback']['pos_feedback'].append(
        [val['posFeedback']])
    queried_data['feedback']['neg_feedback'].append(
        [val['negFeedback']])
    queried_data['sequence'].append([val['sequence']])

    return queried_data


def true_false_type(val, queried_data) -> Dict[Text, List[Any]]:

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
    queried_data['sequence'].append([val['sequence']])

    return queried_data


if __name__ == '__main__':

    subject_list, subjects = get_subjects()

    topic_list, topics_available = get_topics_telegram('var1', 'var2')

    unique_questions = get_questions('sender_id', 'topic_id')
