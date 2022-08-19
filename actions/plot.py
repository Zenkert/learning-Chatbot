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

# values = [66, 19, 6, 5, 4]
list_of_values = [[66, 19, 6, 5, 4], [46, 29, 6, 15, 4], [26, 39, 21, 5, 9]]
values = random.choice(list_of_values)
y = np.array(values)
mylabels = ["Subject 1", "Subject 2",
            "Subject 3", "Subject 4", "Subject 5"]
mycolors = ["#f08663", "#89bcd6", "#ebce90", "#d6ed8b", "#c6b7eb"]

images_folder = '/images/'
my_path = os.path.dirname(os.path.abspath(__file__)) + images_folder


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.0f}%'.format(p=pct)
    return my_autopct


def plot_graph(current_time=dt.now(), path=my_path):

    file_name = f'{current_time}_plot.png'
    final_path = path+file_name
    title = 'DATE: ' + str(current_time.date())
    plt.pie(y, labels=mylabels, colors=mycolors,
            startangle=180, autopct=make_autopct(values))
    plt.title(title)
    plt.savefig(path+file_name)

    return final_path


def image_url(final_path=plot_graph()):

    load_dotenv()

    f = open(final_path, "rb")
    image_data = f.read()

    b64_image = base64.standard_b64encode(image_data)

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

    return parse['data']['link']


if __name__ == '__main__':
    image_url()
