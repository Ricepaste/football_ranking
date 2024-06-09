from bs4 import BeautifulSoup as bs
import requests
import spider as sp


def get_team_records(year=2023):
    '''
    Get the team records for a given year
    '''
    WIDTH = 100

    # Get the team names
    url = f'https://www.sports-reference.com/cfb/years/{year}-schedule.html#'
    web = requests.get(url)

    # print(web.status_code)

    soup = bs(web.text, 'html.parser')

    soup = soup.find('tbody')
    # name = bs(str(soup), "lxml")
    # name = name.find_all('span')
    record = bs(str(soup), "lxml")
    record = bs(str(record.find_all('tr')), "lxml")
    record = record.find_all('td')

    eight = 0
    record_list = []
    temp = []
    same_frenq = 0
    for i in record:
        # print(i.text)
        if (i.text == '1' and same_frenq <= 1):
            same_frenq += 1
            if (same_frenq == 2):
                WIDTH = eight

        if (eight >= WIDTH):
            eight = 0
            record_list.append(temp)
            temp = []
        if (eight == 0 and i.text == '17'):
            break
        temp.append(i.text)
        eight += 1

    # for _ in record_list:
    #     print(_)

    # TODO return the team record in list
    return record_list


def main():
    for i in range(2003, 2024):
        records = get_team_records(i)
        sp.save_to_csv(i, records, "Record")  # type: ignore
    for i in range(2003, 2024):
        ranking = sp.get_year_A(i, "coaches-poll")  # type: ignore
        sp.save_to_csv(i, ranking, "coaches-poll")  # type: ignore
    for i in range(2003, 2024):
        ranking = sp.get_year_B(i)  # type: ignore
        sp.save_to_csv(i, ranking, "ap-poll")  # type: ignore


def debug():
    records = get_team_records(2022)
    # print(records)


if __name__ == '__main__':
    main()
    # debug()
