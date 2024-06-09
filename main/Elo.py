import pandas as pd
import numpy as np
from elosports.elo import Elo
import random

from regex import F


def data_load(year=2003, load='winner'):
    '''
    從資料中讀取出每場的勝者
    註:資料中有些名字有空格,有些名字有括號,有些名字有空格、括號、\xa0
    註:從2013起,勝者出現在第4個column,之前是第3個column

    year: 參數為讀取的年份
    load: 參數為'winner'時可用來讀取勝者，為'loser'時可用來讀取敗者
    '''
    FMT = None
    if load == 'winner':
        FMT = 3
        if year >= 2013:
            FMT = 4
    elif load == 'loser':
        FMT = 6
        if year >= 2013:
            FMT = 7
    # PATH
    path = f"./spider/rank_data/{year}-{year+1}_Record.csv"
    # print(path)
    df = np.array(pd.read_csv(path, sep='\t', header=None))

    winner = df[:, FMT]
    for i in range(winner.size):
        while '\xa0' in winner[i]:
            # print(winner[i])
            winner[i] = winner[i][1:]
        if '(' in winner[i]:
            # print(winner[i])
            winner[i] = winner[i][:winner[i].index('(')]\
                + winner[i][winner[i].index(')')+1:]
            # print(winner[i])
        if ' ' in winner[i]:
            # print(winner[i])
            winner[i] = winner[i][:winner[i].index(' ')]\
                + winner[i][winner[i].index(' ')+1:]
            # print(winner[i])

    return np.array(winner)


def elo_calculate(winner, loser, K=32, epochs=1, shuffle=False, stepLR=True, league=None, schoolset=None):
    '''
    計算所有隊伍的elo值
    註:elo值的計算方式為:elo = elo + k * (result - expected_result)

    winner: 參數為每場比賽的勝者(list)
    loser: 參數為每場比賽的敗者(list)
    K: 參數為elo值的變化率
    epochs: 參數為計算elo值的次數
    shuffle: 參數為是否打亂順序
    stepLR: 參數為是否使用learning rate schduler
    league: 參數為上一年的league
    schoolset: 參數為上一年的schoolset
    '''
    ranking = []
    if league is None:
        eloLeague = Elo(k=K, homefield=0)
    else:
        eloLeague = league
    if schoolset is None:
        school_join = set()
    else:
        school_join = schoolset
        print("Inherit last record...")
        print(school_join)
        print("Processing Elo...")

    for _ in range(epochs):
        # print(f"{_} times")

        # 打亂比賽紀錄訓練順序
        if shuffle:
            # print([(w, l) for w, l in zip(winner, loser)])
            # print()
            start_state = random.getstate()
            random.shuffle(winner)
            random.setstate(start_state)
            random.shuffle(loser)
            # print([(w, l) for w, l in zip(winner, loser)])

        result = zip(winner, loser)
        for w, l in result:
            if not (w in school_join):
                school_join.add(w)
                eloLeague.addPlayer(w)
            if not (l in school_join):
                school_join.add(l)
                eloLeague.addPlayer(l)
            eloLeague.gameOver(winner=w, loser=l, winnerHome=False)
            # print(w, l)

        # learning rate schduler
        if (stepLR):
            eloLeague.k = int(eloLeague.k * 0.9)

    for key, value in sorted((eloLeague.ratingDict).items(), key=lambda x: x[1], reverse=True):
        # print(f"{key:30s}\t{value:.1f}")
        ranking.append([key, value])

    return ranking, eloLeague, school_join


def save_to_csv(year, ranking, poll):
    file_path = "./spider/rank_data/"
    filename = file_path + f"{year}-{year+1}_{poll}.csv"
    print(filename)
    np.savetxt(filename, ranking, encoding='utf-8',
               delimiter="\t", fmt='%s')


def main(EPOCHS=100, K=32, SHUFFLE=False, STEPLR=False, INHERIT=False):

    league = None
    school = None
    for year in range(2003, 2024):
        winner = data_load(year, load='winner')
        loser = data_load(year, load='loser')
        if (INHERIT):
            rank_data, league, school = elo_calculate(
                winner, loser, K=K, epochs=EPOCHS, shuffle=SHUFFLE,
                stepLR=STEPLR, league=league, schoolset=school)
        else:
            rank_data, _, _ = elo_calculate(
                winner, loser, K=K, epochs=EPOCHS, shuffle=SHUFFLE, stepLR=STEPLR)

        save_to_csv(
            year, rank_data, f'elo{EPOCHS}_K{K}_shuffle{SHUFFLE}_stepLR{STEPLR}_inherit{INHERIT}')


def debug():
    EPOCHS = 100
    K = 32
    SHUFFLE = False
    STEPLR = False
    INHERIT = False

    league = None
    school = None
    for year in range(2003, 2024):
        winner = data_load(year, load='winner')
        loser = data_load(year, load='loser')
        if (INHERIT):
            rank_data, league, school = elo_calculate(
                winner, loser, K=K, epochs=EPOCHS, shuffle=SHUFFLE,
                stepLR=STEPLR, league=league, schoolset=school)
        else:
            rank_data, _, _ = elo_calculate(
                winner, loser, K=K, epochs=EPOCHS, shuffle=SHUFFLE, stepLR=STEPLR)

        save_to_csv(
            year, rank_data, f'elo{EPOCHS}_K{K}_shuffle{SHUFFLE}_stepLR{STEPLR}_inherit{INHERIT}')


if __name__ == '__main__':
    # for epoch in [1, 10, 100, 1000]:
    #     for k in [16, 24, 32]:
    #         for inherit in [True, False]:
    #             for steplr in [True, False]:
    main(EPOCHS=10, K=24, SHUFFLE=False, STEPLR=False, INHERIT=False)
    # debug()


# '''
# 計算每場比賽的elo值
# 註:elo值的計算方式為:elo = elo + k*(result - expected_result)
# 註:elo_dict為一個dict,裡面存放著每個球員的elo值

# result: 參數為每場比賽的結果,1為勝,0為敗
# elo_dict: 參數為每個球員的elo值
# k: 參數為elo值的變化率
# '''
# expected_result = 1 / \
#     (1 + 10**((elo_dict['loser'] - elo_dict['winner']) / 400))
# elo_dict['winner'] = elo_dict['winner'] + k*(result - expected_result)
# elo_dict['loser'] = elo_dict['loser'] + k*(expected_result - result)
# return elo_dict
