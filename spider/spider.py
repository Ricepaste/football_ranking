import requests
from bs4 import BeautifulSoup
import numpy as np


def get_year_A(year, poll):
    WIDTH = 8 if poll == "coaches-poll" else 7

    url = f"https://sportsdata.usatoday.com/football/ncaaf/{poll}/{year}-{year+1}"
    res = requests.get(url)
    # print(res.status_code)

    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.find('table')
    # name = BeautifulSoup(str(soup), "lxml")
    # name = name.find_all('span')
    rank = BeautifulSoup(str(soup), "lxml")
    rank = BeautifulSoup(str(rank.find_all('tr')), "lxml")
    rank = rank.find_all('td')

    # for i in name:
    #     print(i.text)

    eight = 0
    ranking = []
    temp = []
    for i in rank:
        # print(i.text)
        if (eight >= WIDTH):
            eight = 0
            ranking.append(temp)
            temp = []
        temp.append(i.text)
        eight += 1

    return ranking


def get_year_B(year):
    WIDTH = 7

    url = f"https://www.espn.com/college-football/rankings/_/poll/1/week/1/year/{year}/seasontype/3"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=hdr)
    # print(res.status_code)

    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.find('tbody')
    # name = BeautifulSoup(str(soup), "lxml")
    # name = name.find_all('span')
    rank = BeautifulSoup(str(soup), "lxml")
    rank = BeautifulSoup(str(rank.find_all('tr')), "lxml")
    name = BeautifulSoup(str(rank.find_all('td')), "lxml")
    rank = rank.find_all('td')

    scl_name = name.select('span.hide-mobile a')
    scl_name = [_.text for _ in scl_name]
    # print(scl_name)

    # rank = BeautifulSoup(str(rank), "lxml")
    # rank = rank.find_all('td')

    # for i in name:
    #     print(i.text)

    eight = 0
    ranking = []
    temp = []
    for i in rank:
        # print(i.text)
        if (eight >= WIDTH):
            eight = 0
            ranking.append(temp)
            temp = []
        if (eight != 1):
            temp.append(i.text)
        else:
            temp.append(scl_name.pop(0))
        eight += 1

    return ranking


def save_to_csv(year, ranking, poll):
    file_path = "./spider/rank_data/"
    filename = file_path + f"{year}-{year+1}_{poll}.csv"
    np.savetxt(filename, ranking, encoding='utf-8', delimiter="\t", fmt='%s')


def debug():
    '''
    Only For Debug Users
    '''
    ranking = get_year_B(2020)
    for _ in ranking:
        print(_)
