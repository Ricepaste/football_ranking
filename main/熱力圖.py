import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

columns = ['RandomWalk', 'Elo', 'Bradley', 'Thurstone', 'AP polls']

#  0: Kendall's tau   1: Spearman's rho
METHOD = 1


def read_csv(year: int, type: str) -> np.ndarray:
    '''
    Parameters:
        year: int, the year of the data
        type: str, options: 'Kendall' or 'Spearman'
    '''
    if type == 'Spearman':
        data = pd.read_csv(
            f"spider/rank_data/{year}-{year+1}_Spearman_correlation_matrix.csv")
    elif type == 'Kendall':
        data = pd.read_csv(
            f"spider/rank_data/{year}-{year+1}_Kendall_correlation_matrix.csv")

    data = np.array(data.drop(columns=['Unnamed: 0']).values)

    return data


def main():
    global columns

    match METHOD:
        case 0:
            title = f"Kendall\'s Tau Correlation Mean Heatmap"
            data_all = []
            for i in range(2019, 2024):
                data_all.append(read_csv(i, 'Kendall'))

            data_array = np.mean(data_all, axis=0)
            # 將0改為nan
            data_array[data_array == 0] = np.nan
            std_dev_array = np.std(data_all, axis=0, ddof=1)
        case 1:
            title = f"Spearman's rho Correlation Mean Heatmap"
            data_all = []
            for i in range(2019, 2024):
                data_all.append(read_csv(i, 'Spearman'))

            data_array = np.mean(data_all, axis=0)
            # 將0改為nan
            data_array[data_array == 0] = np.nan
            std_dev_array = np.std(data_all, axis=0, ddof=1)

    annot_text = [[f'{value:.2f}(σ:{std_dev_array[i][j]:.2f})' if not np.isnan(
        value) else '' for j, value in enumerate(row)] for i, row in enumerate(data_array)]

    plt.figure(figsize=(15, 9))
    heatmap = sns.heatmap(data_array, annot=annot_text, cmap='coolwarm_r',
                          fmt="", xticklabels=columns, yticklabels=columns, annot_kws={"fontsize": 20})
    heatmap.set_title(title, pad=25, fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.show()


if __name__ == '__main__':
    main()
