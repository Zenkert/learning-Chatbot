from email import message
from urllib import request
import wikipediaapi
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import random
import pyjokes

def imsearch(search_word):
    print('-------------------------------------')

    wiki_wiki = wikipediaapi.Wikipedia('en')

    page_py = wiki_wiki.page(search_word)
    print('--------------page_py--------------------')

    if page_py.exists():
        url = page_py.fullurl
        mess = page_py.summary
        if len(mess) < 75:
            mess = 'I couldn\'t find any resources.'
        html = requests.get(url)
        bs = BeautifulSoup(html.text, 'html.parser')

        print('mess: ', mess)
        print('-------------------------------------')

        # project_href = [i['href'] for i in bs.find_all('a', href=True)]

        # ls = []
        # for val in project_href:
        #     if '.jpg' in val:
        #         ls.append(val)

        # if ls:
        #     image = 'https://commons.wikimedia.org' + ls[0]
        
        #     ss = requests.get(image)
        #     soup = BeautifulSoup(ss.text, 'html.parser')
        #     pref = [i['href'] for i in soup.find_all('a', href=True)]

        #     xy = []
        #     for t in pref:
        #         if '.jpg' in t:
        #             xy.append(t)

        #     final_res = xy[0]
        # else:
        #     final_res = ''

        url_link = f'https://unsplash.com/s/photos/{search_word}'
        req = requests.get(url_link)
        data = BeautifulSoup(req.text,'lxml')

        all_image=data.find_all('img')
        print('-------------------------------------')

        emp_ls = []
        i = 1
        for cx in all_image:
            jk = cx['src']
            if 'https://images.unsplash.com/' in jk and i<=5:
                emp_ls.append(jk)
                i+=1 
        
        print('-------------------------------------')
        if emp_ls:
            final_res = random.choice(emp_ls)
            print('final_res: ', final_res)
        else:
            final_res = 'Couldn\'t find an image'
        print('-------------------------------------')
        return mess, final_res
    else:
        mess = ''
        final_res = ''
        return mess, final_res

def joke():

    jokex = pyjokes.get_joke()

    return jokex
    
