from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

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

    topics_available = [top['topic'] for top in topics]

    return topics_available


database = connection(database_name=database_name)
resss = get_subjects(collection_name=collection_name)

# buttons.append(
#     {"payload": '/inform_new{"subj":"'+sub+'"}', "title": sub})
# print(buttons)
