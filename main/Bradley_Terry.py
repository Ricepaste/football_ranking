# import pandas as pd
# import numpy as np

# # df = pd.DataFrame({
# #     'A': [np.nan, 3, 0, 4],
# #     'B': [2, np.nan, 3, 0],
# #     'C': [0, 5, np.nan, 3],
# #     'D': [1, 0, 1, np.nan]
# # }, index=['A', 'B', 'C', 'D'])


# record = pd.read_csv("./spider/rank_data/2022-2023_Record.csv", sep='\t', header=None)

# def deal_team_name(team_name):
#     for i in range(len(team_name)):
#         while '\xa0' in team_name[i]:
#             team_name[i] = team_name[i][1:]
#         if '(' in team_name[i]:
#             team_name[i] = team_name[i][:team_name[i].index('(')]\
#                 + team_name[i][team_name[i].index(')')+1:]
#         if ' ' in team_name[i]:
#             team_name[i] = team_name[i][:team_name[i].index(' ')]\
#                 + team_name[i][team_name[i].index(' ')+1:]
#     return team_name

# all_team_name = list(set(deal_team_name(record[4].values.tolist())
#                                 + deal_team_name(record[7].values.tolist())))
# win_team_name = list(deal_team_name(
#     record[4].values.tolist()))
# lose_team_name = list(deal_team_name(
#     record[7].values.tolist()))

# matrix = [[0 for i in range(len(all_team_name))]
#                 for j in range(len(all_team_name))]

# for i in range(len(win_team_name)):
#     win_index = all_team_name.index(win_team_name[i])
#     lose_index = all_team_name.index(lose_team_name[i])
#     matrix[win_index][lose_index] += 1

# df = pd.DataFrame(matrix, index=all_team_name, columns=all_team_name)

# def get_estimate(i, p, df):
#     get_prob = lambda i, j: np.nan if i == j else p.iloc[i] + p.iloc[j]
#     # 敗場數
#     n = df.iloc[i].sum()

#     # 總場數(敗場數+勝場數)
#     d_n = df.iloc[i] + df.iloc[:, i]

#     # 偏微分過後的值
#     # 公式: Pi = sigma(Wij) / sigma((Wij + Wji) / (Pi + Pj))
#     d_d = pd.Series([get_prob(i, j) for j in range(len(p))], index=p.index)
#     # 總場數除以兩隊實力參數的和
#     d = (d_n / d_d).sum()

#     return n / d

# def estimate_p(p, df):
#     return pd.Series([get_estimate(i, p, df) for i in range(df.shape[0])], index=p.index)

# def iterate(df, p=None, n=20, sorted=True):
#     if p is None:
#         p = pd.Series([1 for _ in range(df.shape[0])], index=list(df.columns))

#     estimates = [p]

#     for _ in range(n):
#         p = estimate_p(p, df)
#         # 這邊除以總和是為了讓機率總和為1(維基是除以幾何平均數) why?
#         p = p / p.sum()
#         estimates.append(p)

#     p = p.sort_values(ascending=False) if sorted else p
#     return p

# # print(iterate(df, n=20, sorted=True))

# if __name__ == '__main__':
#     for year in range(2002, 2023):


import pandas as pd
import numpy as np

# training times
n = 20


class TeamRankEstimator:
    def __init__(self, file_path, output_file):
        self.data_file = file_path
        self.output_file = output_file

    def deal_team_name(self, team_name):
        for i in range(len(team_name)):
            while '\xa0' in team_name[i]:
                team_name[i] = team_name[i][1:]
            if '(' in team_name[i]:
                team_name[i] = team_name[i][:team_name[i].index('(')]\
                    + team_name[i][team_name[i].index(')')+1:]
            if ' ' in team_name[i]:
                team_name[i] = team_name[i][:team_name[i].index(' ')]\
                    + team_name[i][team_name[i].index(' ')+1:]
        return team_name

    def read_data(self, year):
        record = pd.read_csv(self.data_file, sep='\t', header=None)
        win_index = 3
        lose_index = 6
        if year >= 2013:
            win_index = 4
            lose_index = 7

        self.all_team_name = list(set(self.deal_team_name(record[win_index].values.tolist())
                                      + self.deal_team_name(record[lose_index].values.tolist())))
        self.win_team_name = list(self.deal_team_name(
            record[win_index].values.tolist()))
        self.lose_team_name = list(self.deal_team_name(
            record[lose_index].values.tolist()))

    def create_matrix(self):
        matrix = [[0 for _ in range(len(self.all_team_name))]
                  for _ in range(len(self.all_team_name))]

        for win_team, lose_team in zip(self.win_team_name, self.lose_team_name):
            win_index = self.all_team_name.index(win_team)
            lose_index = self.all_team_name.index(lose_team)
            matrix[win_index][lose_index] += 1

        return matrix

    def estimate_rank(self, times, sorted=True):
        df = pd.DataFrame(self.matrix, index=self.all_team_name,
                          columns=self.all_team_name)
        p = pd.Series([1 for _ in range(df.shape[0])], index=list(df.columns))

        estimates = [p]

        for _ in range(times):
            p = self.estimate_p(p, df)
            p = p / p.sum()  # type: ignore
            estimates.append(p)

        p = p.sort_values(ascending=False) if sorted else p
        return p

    def get_estimate(self, i, p, df):
        """
        公式: Pi = sigma(Wij) / sigma((Wij + Wji) / (Pi + Pj)) -> 公式已經經過偏微分
        n: 勝場數 = sigma(Wij)
        d_n: 總場數(敗場數+勝場數)
        d: sigma((Wij + Wji) / (Pi + Pj))
        """
        def get_prob(i, j): return np.nan if i == j else p.iloc[i] + p.iloc[j]
        n = df.iloc[i].sum()
        d_n = df.iloc[i] + df.iloc[:, i]
        d_d = pd.Series([get_prob(i, j) for j in range(len(p))], index=p.index)
        d = (d_n / d_d).sum()

        return n / d

    def estimate_p(self, p, df):
        return pd.Series([self.get_estimate(i, p, df) for i in range(df.shape[0])], index=p.index)

    def write_results(self, rank):
        rank.to_csv(output_file, header=False)

    def excute(self, year):
        self.read_data(year)
        self.matrix = self.create_matrix()
        result = self.estimate_rank(n, sorted=True)
        self.write_results(result)


if __name__ == '__main__':
    for year in range(2019, 2024):
        file_path = f"./spider/rank_data/{year}-{year+1}_Record.csv"
        output_file = f"./spider/rank_data/{year}-{year+1}_Bradley_Terry.csv"
        team_rank_estimator = TeamRankEstimator(file_path, output_file)
        team_rank_estimator.excute(year)
