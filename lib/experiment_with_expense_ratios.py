
from lib.sharpe_ratio_solver import choose_best
import pandas as pd
import matplotlib.pyplot as plt

# I don't think it makes sense to have the solver consider expense ratio and
# dividend yield when solving for factors. So as an alternative, I'll walk down
# the curve where I trade off expense ratio for results. I'll plot this and
# look for any cliffs or plateaus.

def experiment_with_expense_ratios(df, market_type):
    def batch(iterable, batch_size):
        total_size = len(iterable)
        for ndx in range(0, total_size, batch_size):
            yield iterable[ndx:min(ndx + batch_size, total_size)]

    # Order DESC expense ratios, uniqify, split into 20 bins, use the first of
    # each as the "max" expense ratio for the test.
    means_df = pd.DataFrame()
    stdevs_df = pd.DataFrame()
    # ratios_df = pd.DataFrame()
    expense_ratios = df.sort_values(by=['expense_ratio'], ascending=False).expense_ratio.unique()
    batch_size = len(expense_ratios) // 20
    if batch_size == 0:
        raise ValueError(f'Too few expense ratio choices ({len(expense_ratios)})')

    for expense_ratio_batch in batch(expense_ratios, batch_size):
        max_expense_ratio = expense_ratio_batch[0]
        df_this_run = df.copy(deep=True).loc[df.expense_ratio <= max_expense_ratio]
        print(f"\n\nCalculating the best score for {df_this_run.shape[0]} funds where the max expense ratio is {max_expense_ratio}")
        # (mean, stdev, ratio) = choose_best(df_this_run)
        (mean, stdev, _) = choose_best(df_this_run)
        means_df = means_df.append({'expense_ratio': max_expense_ratio, 'mean': mean}, ignore_index=True)
        stdevs_df = stdevs_df.append({'expense_ratio': max_expense_ratio, 'stdev': stdev}, ignore_index=True)
        # ratios_df = ratios_df.append({'expense_ratio': max_expense_ratio, 'ratio': ratio}, ignore_index=True)

    f, ax = plt.subplots()
    ax.set_xlabel('expense ratio')

    means_line, = ax.plot(means_df.expense_ratio, means_df['mean'], 'o', color='blue', label='Mean', linestyle='-')
    stdevs_line, = ax.plot(stdevs_df.expense_ratio, stdevs_df.stdev, 'o', color='red', label='StDev', linestyle='-')
    # ratios_line, = ax.plot(ratios_df.expense_ratio, ratios_df.ratio, 'o', color='purple', label='Ratio', linestyle='-')

    # ax.legend(handles=[means_line, stdevs_line, ratios_line])
    ax.legend(handles=[means_line, stdevs_line])
    plt.savefig(f'plots/expense-ratio-test-{market_type}.png')
    plt.close()
