from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# from dataclasses import dataclass, field
# import collections

database_name = "test"
collection_name = "subjects"


def connection(database_name):
    load_dotenv()
    # user_name = os.getenv('MONGODBUSERNAME')
    # password = os.getenv('MONGODBPASSWORD')
    cluster = f'mongodb+srv://sathish:alpha1234@cluster0.vw63h.mongodb.net/?retryWrites=true&w=majority'

    client = MongoClient(cluster)
    database = client[database_name]
    return database


def get_subjects(collection_name):

    collection = database[collection_name]

    tops = collection.find({})

    # getting subjects from "subjects" collection
    list_of_subjects = [sub["subject"] for sub in tops]

    return list_of_subjects


def get_topics(subject):

    collection = database[collection_name]

    tops = collection.find_one({'subject': f'{subject}'}, '_id')

    subject_id = tops['_id']

    topic_collection = database['topics']

    topics = topic_collection.find({'subId': ObjectId(subject_id)})

    topics_available = {top['topic']: str(top['_id']) for top in topics}

    return topics_available


def get_questions(topic_id):

    collection = database['mcqs']

    topics = collection.find({'topicId': ObjectId(topic_id)})

    queried_data = {'mcq_question': [], 'mcq_choices': [],  'right_answer': [], 'feedback': {
        'pos_feedback': [], 'neg_feedback': []}}
    # qq = [topic for topic in topics]
    for topic in topics:
        try:
            queried_data['mcq_question'].append(topic['mcqs'])
            num_of_options = [topic['option1'], topic['option2']]
            if topic.get('option3', None) != None:
                num_of_options.append(topic['option3'])
                if topic.get('option4', None) != None:
                    num_of_options.append(topic['option4'])
            queried_data['mcq_choices'].append(num_of_options)
            queried_data['right_answer'].append(topic['answer'])
            queried_data['feedback']['pos_feedback'].append(
                topic['posFeedback'])
            queried_data['feedback']['neg_feedback'].append(
                topic['negFeedback'])
        except:
            print('----- ERROR -----')

    question_count = len(queried_data['mcq_question'])
    # return qq
    return question_count, queried_data


database = connection(database_name=database_name)
resss = get_subjects(collection_name=collection_name)

if __name__ == '__main__':
    question_count, queried_data = get_questions('628292ddc942dd68d1fcc42d')
