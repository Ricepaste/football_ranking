import Elo
import random
import numpy as np

"""
此程式用來將比賽資料取前N名的隊伍,並轉換為Thurstone模型的pair2pair資料
實際上必須使用Mplus去跑Thurstone模型,因此此程式只是將資料轉換為Mplus的格式
"""


class TTmodel:
    def __init__(self, teams_amount) -> None:
        self.player_list = []
        self.mu_calculations = {}
        self.mu = None  # shoud be n*1 array
        self.var = 0.5
        self.n = teams_amount
        self.games_amount = 0
        self.ystar = [[] for i in range(self.n * (self.n - 1) // 2)]

        combination = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                temp = [0 for k in range(self.n)]
                temp[i] = 1
                temp[j] = -1
                combination.append(temp)

        self.A = np.array(combination)  # shoud be C_(n,2) * n array
        print(self.A)

    def addPlayer(self, player):
        self.player_list.append(player)

    def gameOver(self, winner, loser):
        if winner not in self.mu_calculations:
            self.mu_calculations[winner] = 1
        else:
            self.mu_calculations[winner] += 1

        if loser not in self.mu_calculations:
            self.mu_calculations[loser] = -1
        else:
            self.mu_calculations[loser] -= 1

        first = self.player_list.index(winner)
        second = self.player_list.index(loser)
        for i in range(len(self.A)):
            if first < second:
                if self.A[i][first] == 1 and self.A[i][second] == -1:
                    self.ystar[i].append("1")
                    break
            else:
                if self.A[i][first] == -1 and self.A[i][second] == 1:
                    self.ystar[i].append("0")
                    break

        self.games_amount += 1

    def fit(self):
        print(self.games_amount)
        self.mu = []
        self.A = np.array(self.A)

        for name in self.player_list:
            self.mu.append(self.mu_calculations[name] / self.games_amount)

        self.mu = np.array(self.mu)
        self.mu = self.mu / ((1 + 2 * self.var) ** 0.5)
        self.mu = self.mu.reshape((self.mu.shape[0], 1))
        self.var = self.var / (1 + 2 * self.var)
        # print(self.mu)

        maxx = 0
        for i in range(len(self.ystar)):
            if len(self.ystar[i]) > maxx:
                maxx = len(self.ystar[i])

        for i in range(len(self.ystar)):
            while len(self.ystar[i]) < maxx:
                self.ystar[i].append(".")

        for i in range(len(self.ystar)):
            temp = self.ystar[i].copy()
            for j in range(10):
                self.ystar[i] += temp

        # for i in range(len(self.ystar)):
        #     temp = [0, 1]
        #     self.ystar[i] += temp

        for i in range(len(self.ystar)):
            for j in range(len(self.ystar[i])):
                if self.ystar[i][j] == ".":
                    self.ystar[i][j] = str(random.randint(0, 1))

        self.ystar = np.array(self.ystar).T

        for j in range(len(self.ystar[len(self.ystar) - 1])):
            if self.ystar[len(self.ystar) - 1][j] == "0":
                self.ystar[len(self.ystar) - 1][j] = "1"
            else:
                self.ystar[len(self.ystar) - 1][j] = "0"

        print(self.ystar)
        print(self.n)
        save_to_csv("test", self.ystar)


def save_to_csv(name, ranking):
    file_path = "./spider/thurstone/"
    filename = file_path + f"{name}.dat"
    print(filename)
    np.savetxt(filename, ranking, encoding="utf-8", delimiter=" ", fmt="%s")


def load_elo_top_N(year, N):
    filename = ".\\spider\\rank_data\\"
    filename += f"{year}-{year+1}_elo10_K24_shuffleFalse_stepLRFalse_inheritFalse.csv"
    with open(filename, "r") as f:
        lines = f.readlines()
    lines = lines[0:N]
    lines = [line.split()[0] for line in lines]
    return lines


def TT_calculate(
    winner,
    loser,
    K=32,
    epochs=1,
    shuffle=False,
    stepLR=True,
    league=None,
    schoolset=None,
    top10=None,
):
    """
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
    """

    top_winner = []
    top_loser = []
    for w, l in zip(winner, loser):
        if (w in top10) and (l in top10):
            top_winner.append(w)
            top_loser.append(l)

    if top10 is None:
        all_team = set(winner)
        all_team.update(set(loser))
    else:
        all_team = set(top_winner)
        all_team.update(set(top_loser))
        winner = top_winner
        loser = top_loser

    n = len(all_team)
    ranking = []
    if league is None:
        TTLeague = TTmodel(n)
    else:
        TTLeague = league
    if schoolset is None:
        school_join = set()
    else:
        school_join = schoolset
        print("Inherit last record...")
        print(school_join)
        print("Processing...")

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
                TTLeague.addPlayer(w)
            if not (l in school_join):
                school_join.add(l)
                TTLeague.addPlayer(l)
            TTLeague.gameOver(winner=w, loser=l)
        TTLeague.fit()
        print(TTLeague.player_list)

        # MU = list(TTLeague.mu)
        # biggest = max(MU)
        # # while biggest in MU:
        # for _ in range(10):
        #     biggest = max(MU)
        #     index = MU.index(biggest)
        #     MU.pop(index)
        #     name = TTLeague.player_list.pop(index)
        #     print(biggest)
        #     print(name)
        #     print(TTLeague.mu_calculations[name])

    #     # learning rate schduler
    #     if (stepLR):
    #         TTLeague.k = int(TTLeague.k * 0.9)
    print()

    # for key, value in sorted((TTLeague.ratingDict).items(), key=lambda x: x[1], reverse=True):
    #     # print(f"{key:30s}\t{value:.1f}")
    #     ranking.append([key, value])

    # return ranking, TTLeague, school_join


def main(EPOCHS=100, K=32, SHUFFLE=False, STEPLR=False, INHERIT=False):

    league = None
    school = None
    for year in range(2023, 2024):
        winner = Elo.data_load(year, load="winner")
        loser = Elo.data_load(year, load="loser")

        if INHERIT:
            # rank_data, league, school = TT_calculate(
            #     winner, loser, K=K, epochs=EPOCHS, shuffle=SHUFFLE,
            #     stepLR=STEPLR, league=league, schoolset=school)
            TT_calculate(
                winner,
                loser,
                K=K,
                epochs=EPOCHS,
                shuffle=SHUFFLE,
                stepLR=STEPLR,
                league=league,
                schoolset=school,
                top10=load_elo_top_N(year, 20),
            )
        else:
            # rank_data, _, _ = TT_calculate(
            #     winner, loser, K=K, epochs=EPOCHS, shuffle=SHUFFLE, stepLR=STEPLR)
            TT_calculate(
                winner,
                loser,
                K=K,
                epochs=EPOCHS,
                shuffle=SHUFFLE,
                stepLR=STEPLR,
                top10=load_elo_top_N(year, 20),
            )

        # Elo.save_to_csv(
        #     year, rank_data, f'elo{EPOCHS}_K{K}_shuffle{SHUFFLE}_stepLR{STEPLR}_inherit{INHERIT}')


if __name__ == "__main__":
    main()
