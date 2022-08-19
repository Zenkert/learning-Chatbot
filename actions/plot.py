import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime as dt
import os

import base64
import json
import requests
from dotenv import load_dotenv
import os
import random
import pathlib


# values = [66, 19, 6, 5, 4]


def random_value():
    list_of_values = [[66, 19, 6, 5, 4], [46, 29, 6, 15, 4], [26, 39, 21, 5, 9],
                      [96, 1, 1, 1, 1], [6, 49, 26, 10, 9], [16, 49, 11, 5, 19]]

    values = random.choice(list_of_values)
    y = np.array(values)
    mylabels = ["Subject 1", "Subject 2",
                "Subject 3", "Subject 4", "Subject 5"]
    mycolors = ["#f08663", "#89bcd6", "#ebce90", "#d6ed8b", "#c6b7eb"]

    return values, y, mylabels, mycolors


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.0f}%'.format(p=pct)
    return my_autopct


def plot_graph(current_time):

    file_name = f'{current_time}_plot.png'
    title = 'DATE: ' + str(current_time.date())

    # values, y, mylabels, mycolors = random_value()

    # plt.pie(y, labels=mylabels, colors=mycolors,
    #         startangle=180, autopct=make_autopct(values))
    # plt.title(title)
    # plt.savefig(file_name)
    # return file_name

    subjects = ['Biology', 'Math', 'Art and Design',
                'Humanities', 'Business']

    list_of_values = [[66, 19, 6, 5, 4], [46, 29, 6, 15, 4], [26, 39, 21, 5, 9],
                      [96, 1, 1, 1, 1], [6, 49, 26, 10, 9], [16, 49, 11, 5, 19]]

    values = random.choice(list_of_values)

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


def image_url(current_time):

    load_dotenv()

    final_path = plot_graph(current_time)
    with open(final_path, "rb") as f:
        image_data = f.read()

    b64_image = base64.standard_b64encode(image_data)

    os.remove(final_path)

    client_id = os.getenv('CLIENT_ID')
    headers = {'Authorization': 'Client-ID ' + client_id}

    data = {'image': b64_image, 'title': 'test'}

    request = requests.post(url="https://api.imgur.com/3/upload.json",
                            data=data, headers=headers)

    if request.status_code != 200:
        # return error message
        error_image = 'https://imobie-resource.com/en/support/img/sorry-there-was-a-problem-with-your-request-1.jpg'
        return error_image

    parse = json.loads(request.text)

    return final_path, parse['data']['link']


if __name__ == '__main__':
    image_url(current_time=dt.now())
