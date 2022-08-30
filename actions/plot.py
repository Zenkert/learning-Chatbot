import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime as dt
import os

import base64
import json
import requests
from dotenv import load_dotenv
import os
import pandas as pd
from collections import Counter
from typing import List, Tuple


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.0f}%'.format(p=pct)
    return my_autopct


def plot_graph(user_id, current_time):

    file_name = f'{current_time}_plot.png'
    title = 'DATE: ' + str(current_time.date())

    student_data = pd.read_excel('actions/student_db_new.xlsx')
    student_data = student_data.loc[:, ~
                                    student_data.columns.str.contains('^Unnamed')]  # removing "Unnamed" column

    subjects = ['Biology', 'Math', 'Art and Design',  # default subjects
                'Humanities', 'Business']

    values = [0, 0, 0, 0, 0]  # default scores

    try:
        subjects = []
        values = []

        # iterating over rows
        for index, row in student_data.iterrows():
            if str(row['User']) == str(user_id):
                current_row = row.to_dict()  # converting row to dictionary
                # popping <'User':value> since it is not utilized in graph
                current_row.pop('User')
                # finding top 5 values in the dictionary
                largest_values: List[Tuple] = Counter.most_common(
                    current_row, 5)

        # largest_values: List[Tuple] = [(a,b), (c,d), ...]
        for value in largest_values:
            subjects.append(value[0])  # value[0] = subject
            values.append(int(value[1]))  # value[1] = score
    except:
        pass

    colors = ["#f08663", "#89bcd6", "#ebce90", "#d6ed8b", "#c6b7eb"]
    fig = plt.figure(figsize=(10, 5))

    plt.bar(subjects, values, color=colors,
            width=0.4)

    plt.xlabel("Subjects")
    plt.ylabel("Activity completed related to Subject(no of times)")
    plt.title(title)
    plt.savefig(file_name)
    # plt.show()
    return file_name


def image_url(user_id, current_time):

    load_dotenv()

    final_path = plot_graph(user_id, current_time)
    with open(final_path, "rb") as f:
        image_data = f.read()

    b64_image = base64.standard_b64encode(image_data)

    # removing image from storage since it is not needed to be stored
    os.remove(final_path)

    client_id = os.getenv('CLIENT_ID')
    headers = {'Authorization': 'Client-ID ' + client_id}

    data = {'image': b64_image, 'title': 'test'}

    request = requests.post(url="https://api.imgur.com/3/upload.json",
                            data=data, headers=headers)

    if request.status_code != 200:
        # return error message if unsuccessful
        error_image = 'https://imobie-resource.com/en/support/img/sorry-there-was-a-problem-with-your-request-1.jpg'
        return error_image

    parse = json.loads(request.text)

    return final_path, parse['data']['link']


if __name__ == '__main__':
    image_url(user_id='', current_time=dt.now())
