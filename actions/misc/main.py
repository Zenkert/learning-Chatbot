from pymongo import MongoClient
from dotenv import load_dotenv
import os

# from dataclasses import dataclass, field
# import collections

database_name = "test"
collection_name = "mcqs"

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
    i = 0
    for z in tops:
        if i <= 5:
            l.append(z['mcqs'])
        i += 1
    misc = collection.find()
    for m in misc[0]:
        print(m)

    return l

database = connection(database_name=database_name)
resss = get_subjects(collection_name=collection_name)
# print(resss)

# def get_subjects():
    
#     quesz = connection()
#     tops = quesz.find({})
        
#     l = []
#     for z in tops:
#         l.append(z['category'])

#     x = collections.Counter(l)
#     y = x.most_common(10) # even value

#     subjects = []
#     for val in y:
#         sub = val[0]
#         subjects.append(sub)
#     # print("Subjects: ", subjects)

#     no_of_groups = 2 # constant value
#     slice_value = int(len(subjects)/no_of_groups)

#     subject_group1 = subjects[:slice_value]
#     subject_group1.append("Other options")
    
#     subject_group2 = subjects[slice_value:]
    
#     return quesz, subject_group1, subject_group2


# def get_questions(xyz):
#     quesz, _, _ = get_subjects()

#     documents_chosen = quesz.find({'category' : xyz})
#     questions_chosenx = []
#     choicex = []
#     correct_answerx = []

#     for ques in documents_chosen:
#         questions_chosenx.append(ques['question'])
#         choicex.append(ques['choices'])
#         correct_answerx.append(ques['correct_answer'])
    
#     # print("Questions: ", questions_chosenx)
#     # print("Choices: ", choicex)
#     # print("Correct_answer: ", correct_answerx)

#     return questions_chosenx, choicex, correct_answerx



