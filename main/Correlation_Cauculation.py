import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import random

# METHOD = 0: Kendall's tau, METHOD = 1: Spearman's rank
METHOD = 0

rank_object = ['_random_walk_matrix_Flash0.0001_CON0.1_INIT0.01.csv',
               '_elo10_K24_shuffleFalse_stepLRFalse_inheritFalse.csv',
               '_Bradley_Terry.csv',
               '_TTU.csv',
               '_ap-poll.csv',
               ]

rank_name = ['Random Walk', 'Elo', 'Bradley-Terry', 'TTU', 'AP Poll']

team_name = {
    'TCU': 'TexasChristian',
    'USC': 'SouthernCalifornia',
    'LSU': 'LouisianaState',
    'BYU': 'BrighamYoung',
    'UCF': 'CentralFlorida',
    'NCState': 'NorthCarolina State',
    'SanJoseState': 'SanJose State',
    "Hawai'i": "Hawaii",
    "OleMiss": "Mississippi",
}


def deal_team_name(rank):
    '''
    處理隊伍名稱
    '''
    for i in range(len(rank)):
        if rank[i] in team_name:
            rank[i] = team_name[rank[i]]
        if ' ' in rank[i]:
            rank[i] = rank[i].replace(' ', '')

    return rank


def Kendall_tau(array1, array2):
    '''
    計算兩個排名的相似度
    註:Kendall tau係數的計算方式為:
    tau = (P-Q)/(P+Q)
    P: 有相同排名的對數
    Q: 沒有相同排名的對數
    '''

    P = 0
    Q = 0
    for i in range(min(len(array1), len(array2))):
        for j in range(min(len(array1), len(array2))):
            if (array1[i] > array1[j] and array2[i] > array2[j]) or (array1[i] < array1[j] and array2[i] < array2[j]):
                P += 1
            else:
                Q += 1
    tau = (P-Q)/(P+Q)
    return tau


def Spearman_rank(array1, array2):
    max_len = max(len(array1), len(array2))
    if len(array1) < max_len:
        for i in range(max_len-len(array1)):
            array1.append(random.randint(1, 2*max_len))
    elif len(array2) < max_len:
        for i in range(max_len-len(array2)):
            array2.append(random.randint(1, 2*max_len))

    correlation, p_value = spearmanr(array1, array2)
    return correlation


Form = []
for year in range(2019, 2024):
    corr = []
    corr_matrix = np.zeros((len(rank_name), len(rank_name)))
    for k in range(len(rank_object)-1):
        for l in range(k+1, len(rank_object)):
            try:
                rank1 = pd.read_csv(
                    f'./spider/rank_data/{year}-{year+1}{rank_object[k]}', sep=',', header=None)
                rank2 = pd.read_csv(
                    f'./spider/rank_data/{year}-{year+1}{rank_object[l]}', sep=',', header=None)

                # 處理elo \t
                if k == 1:
                    rank1 = pd.read_csv(
                        f'./spider/rank_data/{year}-{year+1}{rank_object[k]}', sep='\t', header=None)
                elif l == 1:
                    rank2 = pd.read_csv(
                        f'./spider/rank_data/{year}-{year+1}{rank_object[l]}', sep='\t', header=None)

                rank1_arr = [rank1.values.tolist()[i][0].rstrip()
                             for i in range(len(rank1.values.tolist()))]
                rank2_arr = [rank2.values.tolist()[i][0].rstrip()
                             for i in range(len(rank2.values.tolist()))]

                rank1_arr = deal_team_name(rank1_arr)
                rank2_arr = deal_team_name(rank2_arr)

                if k == 4:
                    rank1 = pd.read_csv(
                        f'./spider/rank_data/{year}-{year+1}{rank_object[k]}', sep='\t', header=None)
                    # get the second column and turn to list
                    rank1 = rank1.iloc[:, 1].values.tolist()
                    rank1_arr = deal_team_name(rank1)

                elif l == 4:
                    rank2 = pd.read_csv(
                        f'./spider/rank_data/{year}-{year+1}{rank_object[l]}', sep='\t', header=None)

                    # get the second column and turn to list
                    rank2 = rank2.iloc[:, 1].values.tolist()
                    rank2_arr = deal_team_name(rank2)

                for i in range(min(len(rank1_arr), len(rank2_arr))):
                    try:
                        rank2_arr[i] = rank1_arr.index(rank2_arr[i])+1
                    except:
                        rank2_arr[i] = 1000

                for i in range(len(rank1_arr)):
                    rank1_arr[i] = i+1

                if METHOD == 0:
                    rank_correlation = Kendall_tau(rank1_arr, rank2_arr)
                if METHOD == 1:
                    rank_correlation = Spearman_rank(rank1_arr, rank2_arr)

                corr.append(rank_correlation)

                # 將相關係數填入矩陣
                corr_matrix[k][l] = rank_correlation
                corr_matrix[l][k] = rank_correlation  # 矩陣是對稱的

                print("File read successfully")
                print(
                    f"{rank_name[k]}_{rank_name[l]} Compare: ", rank_correlation)
                # print(f"{year}-{year+1} 年度 Kendall tau係數 : ", rank_correlation)
            except:
                print("File not found")
                assert False, "找不到拉乾"
    corr_df = pd.DataFrame(corr_matrix, index=rank_name, columns=rank_name)
    # 將 DataFrame 保存到 CSV 文件
    if METHOD == 1:
        corr_df.to_csv(
            f'./spider/rank_data/{year}-{year+1}_Spearman_correlation_matrix.csv')
    if METHOD == 0:
        corr_df.to_csv(
            f'./spider/rank_data/{year}-{year+1}_Kendall_correlation_matrix.csv')

# for i in Form:
#     print(i)
