import requests
import urllib
import time
import os
from threading import Thread
from bs4 import BeautifulSoup

characteristic_word = '空空如也'

article_url = list()


def select_all_article_url(check_url):
    i = 1
    filter_str = '{}article/details/'.format(check_url, )
    while True:
        page_url = '{}article/list/{}'.format(check_url, i)
        response = urllib.request.urlopen(page_url)
        page_info = response.read().decode('utf-8')
        if characteristic_word in page_info:
            break
        else:
            soup = BeautifulSoup(page_info, 'lxml')
            for son_url in soup.find_all('a'):
                if not son_url.get('href', None):
                    continue
                if (filter_str in son_url.get('href')) and (son_url.get('href') not in article_url):
                    article_url.append(son_url.get('href'))
        i += 1


def get_url(index_url):
    if len(article_url) == 0:
        select_all_article_url(index_url)
    thread_list = list()
    for _ in range(8):
        thread_obj = Thread(target=method_name, args=())
        thread_list.append(thread_obj)
    for obj in thread_list:
        obj.start()


def method_name():
    i = 1
    while True:
        print('这是第{}波访问'.format(i))
        for _url in article_url:
            requests.get(_url)
        time.sleep(5)
        i += 1
        if os.path.isfile(r'F:\flashclient\logs\stop.txt'):
            break


if __name__ == '__main__':
    main_url = 'https://blog.csdn.net/mingtiannihaoabc/'
    get_url(main_url)