from lib.sharpe_ratio_solver import choose_best
from lib.chosen_summarizer import ChosenSummarizer
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def experiment_with_shuffling(df, market_type):
    results_df = pd.DataFrame()
    chosen_summarizers = []

    for i in range(0, 100):
        print(i)
        # Randomly sample 80% of the data
        chosen_summarizer = choose_best(df.sample(frac=0.8))
        expense_ratio = chosen_summarizer.summarize(relevant_columns=['expense_ratio']).expense_ratio
        results_df = results_df.append(
            {
                'mean': chosen_summarizer.mean(),
                # 'stdev': chosen_summarizer.stdev(),
                'sharpe_ratio': chosen_summarizer.sharpe_ratio(),
                'sharpe_ratio_to_expense_ratio': chosen_summarizer.sharpe_ratio() / expense_ratio
            },
            ignore_index=True
        )
        chosen_summarizers.append(chosen_summarizer)

    results_df = results_df.sort_values(by=['sharpe_ratio_to_expense_ratio'])

    _, axs = plt.subplots(2, 1, sharex=True)
    means_line, = axs[0].plot(results_df.sharpe_ratio_to_expense_ratio, results_df['mean'], 'o', color='blue', label='Mean', linestyle='-')
    stdevs_line, = axs[1].plot(results_df.sharpe_ratio_to_expense_ratio, results_df.sharpe_ratio, 'o', color='red', label='Sharpe Ratio', linestyle='-')
    for ax in axs:
        ax.legend(handles=[means_line, stdevs_line])
        ax.set_xlabel('sharpe_ratio_to_expense_ratio')

    plt.savefig(f'plots/shuffling-test-{market_type}.png')
    plt.close()

    for i in results_df.sort_values(by=['sharpe_ratio_to_expense_ratio'], ascending=False).round(3).head().index:
        print(chosen_summarizers[i].summary())
        print()
