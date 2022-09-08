# from urllib import response
import requests
import json

from operator import itemgetter

from actions.enum_uniques import ID


# with open('responses.json', 'r') as file:
#     data = json.load(file)
with open('actions/responses.json', 'r') as file:
    data = json.load(file)


english_subjects = ['Business', 'Chemistry', 'Psychology', 'Technology', 'Language',
                    'Math', 'History', 'Biology', 'Physics', 'Humanities', 'Art and Design']


def chunks(list_to_chunk, length):

    # looping till length of the list_to_chunk
    for i in range(0, len(list_to_chunk), length):
        yield list_to_chunk[i:i + length]


def get_subjects():
    response = requests.get(
        'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/subject/get').json()

    subject_list = [s['subject'] for s in response]

    subjects = [(s['subject'], s['_id']) for s in response]

    subjects_chunk = list(chunks(subjects, ID.SUBJECT_BUTTONS.value))

    return subject_list, subjects_chunk


def get_topics(subject, language):
    subject_response = requests.get(
        'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/subject/get').json()

    for s in subject_response:
        if s['subject'] == subject:
            subject_id = s['_id']

    response = requests.get(
        'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/topic').json()

    topic_list = [s['topic']
                  for s in response if s['subId'] == subject_id and s["language"] == ID[language].value]

    topics = [(s['topic'], s['_id'])
              for s in response if s['subId'] == subject_id and s["language"] == ID[language].value]

    topics_chunk = list(chunks(topics, ID.TOPIC_BUTTONS.value))

    return topic_list, topics_chunk


def get_questions(topic_id):

    response = requests.get(
        f'http://ec2-3-71-216-21.eu-central-1.compute.amazonaws.com:5000/api/topic/getByTopic/{topic_id}').json()

    queried_data = {'mcq_question': [], 'mcq_choices': [], 'file': [], 'right_answer': [], 'feedback': {
        'pos_feedback': [], 'neg_feedback': []}}

    question_count = 0

    for value in response:
        get_all_questions = value['allQuestions']
        all_questions = sorted(get_all_questions, key=itemgetter(
            'sequence'), reverse=False)  # sorted by sequence number

        for val in all_questions:
            if val['questionType'] == 'mcqs':
                question_count += 1
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

    return question_count, queried_data


if __name__ == '__main__':
    subject_list, subjects = get_subjects()
    print(subject_list, subjects)

    topic_list, topics_available = get_topics('Art and Design', 'DE')
    print(topic_list, topics_available)

    # question_count, queried_data = get_questions(
    #     '6315ff84c9b400710c0ebea6')
    # print(question_count, queried_data)
