import os
import json
import base64
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime as dt
from typing import Any, Text, Dict, List, Tuple

from actions.enum_uniques import Id


def plot_graph(user_id, user_language, current_time) -> Text:

    show_num_of_subjects = Id.PLOT_GRAPH_NUM_OF_SUBJECTS.value

    date_response = {
        'EN': 'DATE',
        'DE': 'DATUM',
        'EL': 'ΗΜΕΡΟΜΗΝΙΑ',
        'ES': 'FECHA'
    }
    xaxis_response = {
        'EN': f'Top {show_num_of_subjects} Subjects',
        'DE': f'Top {show_num_of_subjects} Fächer',
        'EL': f'{show_num_of_subjects} κορυφαία θέματα',
        'ES': f'Las {show_num_of_subjects} mejores asignaturas'
    }
    yaxis_response = {
        'EN': 'Activity completed related to Subject(no of times)',
        'DE': 'Abgeschlossene Aktivität im Zusammenhang mit dem Subjekt',
        'EL': 'Δραστηριότητα που ολοκληρώθηκε σε σχέση με το θέμα',
        'ES': 'Actividad realizada relacionada con la asignatura'
    }

    file_name = f'{current_time}_plot.png'
    title = f'{date_response[user_language]}: ' + str(current_time.date())

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
                # finding top n = {show_num_of_subjects} values in the dictionary
                largest_values: List[Tuple] = Counter.most_common(
                    current_row, show_num_of_subjects)

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

    plt.xlabel(f'{xaxis_response[user_language]}')
    plt.ylabel(f'{yaxis_response[user_language]}')
    plt.title(title)
    plt.savefig(file_name)
    # plt.show()
    return file_name


def image_url(user_id, user_language, current_time) -> Tuple[Text, Text]:

    load_dotenv()

    final_path = plot_graph(user_id, user_language, current_time)
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
    image_url(user_id='', user_language='EN', current_time=dt.now())
