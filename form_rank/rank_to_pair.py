import pandas as pd
import numpy as np


def read_csv(filename: str = './form_rank/Football_Ranking.csv') -> pd.DataFrame:
    df = pd.read_csv(filename, delimiter=',')
    return df[1:]


def extract_rank() -> np.ndarray:
    idx = ["1st", "2nd", "3rd", "4th"]
    df = read_csv()
    all_rank = []
    for i in range(2019, 2024):
        year_rank = []
        for j in idx:
            temp = list(df[f"{i} - {i+1} [{j}]"])
            year_rank.append(temp)
        all_rank += list(np.array(year_rank).T)
    all_rank = np.array(all_rank)

    return all_rank


def ranking_to_pair(ranking: np.ndarray) -> np.ndarray:
    pair = []
    for i in range(len(ranking)):
        temp = []
        if ('nan' in ranking[i]):
            continue
        for j in range(len(ranking[i])):
            for k in range(j+1, len(ranking[i])):
                if (np.where(ranking[i] == f'Method {j+1}')[0] < np.where(ranking[i] == f'Method {k+1}')[0]):
                    temp.append(1)
                else:
                    temp.append(0)
        pair.append(temp)

    return np.array(pair)


def save_csv(filename: str, data: np.ndarray):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, header=False)


def main():
    ranking = extract_rank()
    pair = ranking_to_pair(ranking)
    save_csv('./form_rank/pair.csv', pair)


if __name__ == '__main__':
    main()
