from pymongo import MongoClient
from dotenv import load_dotenv
import os

# from dataclasses import dataclass, field
# import collections

database_name = "test"
collection_name = "subjects"

def connection(database_name):
    load_dotenv()
    user_name = os.getenv('MONGODBUSERNAME')
    password = os.getenv('MONGODBPASSWORD')
    cluster = f'mongodb+srv://{user_name}:{password}@cluster0.vw63h.mongodb.net/?retryWrites=true&w=majority'

    client = MongoClient(cluster)
    database = client[database_name]
    return database

def get_subjects(collection_name):
    
    collection = database[collection_name]

    tops = collection.find({})
        
    l = []
    i = 1
    for z in tops:
        if i <= 5:
            l.append(z['subject'])
        i += 1

    return l 

database = connection(database_name=database_name)
resss = get_subjects(collection_name=collection_name)
print(resss)



