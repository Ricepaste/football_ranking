import pandas as pd
import numpy as np
import csv


FLASH = 0.0001
CONVERGENCE = 0.1


def deal_team_name(team_name):
    for i in range(len(team_name)):
        # 去除隊名中的空白和括號中的內容(含括號)
        if '\xa0' in team_name[i]:
            team_name[i] = team_name[i].replace('\xa0', '')
        if '(' in team_name[i]:
            while '(' in team_name[i]:
                start = team_name[i].find('(')
                end = team_name[i].find(')')
                team_name[i] = team_name[i][:start] + team_name[i][end+1:]
    return team_name


# 例外狀況 有比賽被取消，比分先暫定0:0 (手動加上比分)
# 3	Sep 14, 2013	2:00 PM	Sat	Fresno State		@	Colorado		Game Cancelled
# 1	Sep 5, 2015	7:30 PM	Sat	McNeese State		@	(14) Louisiana State		Cancelled due to weather


for year in range(2023, 2024):
    # for year in range(2023, 2024):

    record = pd.read_csv(
        f'./spider/rank_data/{year}-{year+1}_Record.csv', sep="\t", header=None)

    if year < 2013:
        team_index = 3
        score_index = 4
    else:
        team_index = 4
        score_index = 5

    # team name
    # get the col4 and col7 of the record and combine them into a list
    header = record.columns[team_index]
    win_team_name = record[team_index]
    win_team_name = win_team_name.dropna()
    win_team_name = win_team_name.tolist()
    win_team_name = deal_team_name(win_team_name)

    header = record.columns[team_index+3]
    lose_team_name = record[team_index+3]
    lose_team_name = lose_team_name.dropna()
    lose_team_name = lose_team_name.tolist()
    lose_team_name = deal_team_name(lose_team_name)
    # print(len(set(lose_team_name)))

    # use list to store the team name and delete the duplicate team name
    all_team_name = sorted(list(set(win_team_name + lose_team_name)))
    # print(all_team_name)

    # build a 2D list to store the lose-win matrix
    matrix = [[0.0 for i in range(len(all_team_name))]
              for j in range(len(all_team_name))]

    # 計算單支隊伍敗場數
    lose_count = {}
    for i in range(len(lose_team_name)):
        if lose_team_name[i] not in lose_count:
            lose_count[lose_team_name[i]] = 1
        else:
            lose_count[lose_team_name[i]] += 1

    # # 對於輸過的隊伍，計算走到該隊伍的機率
    # for i in range(len(win_team_name)):
    #     win_index = all_team_name.index(win_team_name[i])
    #     lose_index = all_team_name.index(lose_team_name[i])
    #     probability = (1-0.001*(len(all_team_name) -
    #                    lose_count[lose_team_name[i]]))/lose_count[lose_team_name[i]]

    #     if (matrix[lose_index][win_index] != 0.001):
    #         matrix[lose_index][win_index] += probability
    #     else:
    #         matrix[lose_index][win_index] = probability
    for i in range(len(win_team_name)):
        matrix[all_team_name.index(lose_team_name[i])
               ][all_team_name.index(win_team_name[i])] += 1

    # 對矩陣每一列做MinMaxScaler
    for i in range(len(matrix)):
        row_max = max(matrix[i])
        row_min = min(matrix[i])
        for j in range(len(matrix)):
            try:
                matrix[i][j] = (matrix[i][j] - row_min) / (row_max - row_min)
            except:
                continue

    # 使矩陣每列總和為1
    try:
        for i in range(len(matrix)):
            row_sum = sum(matrix[i])
            try:
                matrix[i] = [x / row_sum for x in matrix[i]]
            except:
                continue
    except Exception as e:
        print(matrix[i])
        print(e)

    # 每個元素加上閃現機率
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] == 0 and i != j:
                matrix[i][j] += FLASH

    # 使矩陣每列總和為1
    for i in range(len(matrix)):
        row_sum = sum(matrix[i])
        try:
            matrix[i] = [x / row_sum for x in matrix[i]]
        except:
            continue

    # ----------------------------------------------
    '''
    TAG: print matrix
    '''
    # print("\t", end='')
    # for i in range(len(all_team_name)):
    #     print(all_team_name[i], end='\t')
    # print()

    # for i in range(len(all_team_name)):
    #     print(all_team_name[i], end='\t')
    #     for j in range(len(all_team_name)):
    #         print(f"{matrix[i][j]:.5f}", end='\t')
    #     print()
    # 檢查矩陣列和是否接近1
    # for i in range(len(all_team_name)):
    #     sum = 0
    #     for j in range(len(all_team_name)):
    #         sum += matrix[i][j]
    #     print(all_team_name[i], sum)
    # if (sum < 0.9):
    #     print(all_team_name[i], sum)
    # ----------------------------------------------

    # turn matrix to numpy array
    matrix = np.array(matrix)
    # print(matrix)

    # 給定初始狀態，求穩定態
    state = np.array([1/len(all_team_name) for i in range(len(all_team_name))])
    state = state.dot(matrix)
    while (np.linalg.norm(state - state.dot(matrix)) > 0.0001):
        state = state.dot(matrix)
    # print(state)

    # 印出對應隊伍，前十名
    state = state.tolist()
    state = list(zip(all_team_name, state))
    state.sort(key=lambda x: x[1], reverse=True)

    # 印出state和all_team_name
    # for i in range(len(state)):
    #     print(state[i])

    # save to csv
    with open(f'./spider/rank_data/{year}-{year+1}_random_walk_matrix.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(['team', 'state'])
        for i in range(len(state)):
            writer.writerow([state[i][0], state[i][1]])
