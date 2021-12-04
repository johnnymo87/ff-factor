
from lib.sharpe_ratio_solver import choose_best
import pandas as pd
import matplotlib.pyplot as plt

# I don't think it makes sense to have the solver consider expense ratio and
# dividend yield when solving for factors. So as an alternative, I'll walk down
# the curve where I trade off expense ratio for results. I'll plot this and
# look for any cliffs or plateaus.

def experiment_with_biased_expense_ratios(df, market_type):
    def batch(iterable, batch_size):
        total_size = len(iterable)
        for ndx in range(0, total_size, batch_size):
            yield iterable[ndx:min(ndx + batch_size, total_size)]

    # Order DESC expense ratios, uniqify, split into 20 bins, use the first of
    # each as the "max" expense ratio for the test.
    expense_ratios = df.sort_values(by=['expense_ratio'], ascending=False).expense_ratio.unique()
    batch_size = len(expense_ratios) // 20
    if batch_size == 0:
        raise ValueError(f'Too few expense ratio choices ({len(expense_ratios)})')
    max_expense_ratios =\
         [expense_ratio_batch[0] for expense_ratio_batch in batch(expense_ratios, batch_size)]

    def experiment(weights_and_biases):
        means_df = pd.DataFrame()
        stdevs_df = pd.DataFrame()

        for max_expense_ratio in max_expense_ratios:
            df_this_run = df.copy(deep=True).loc[df.expense_ratio <= max_expense_ratio]
            print(f"\n\nCalculating the best score for {df_this_run.shape[0]} funds where the max expense ratio is {max_expense_ratio} and weights and biases are {weights_and_biases}")
            (mean, stdev, _) = choose_best(df_this_run, weights_and_biases=weights_and_biases)
            means_df = means_df.append({'expense_ratio': max_expense_ratio, 'mean': mean}, ignore_index=True)
            stdevs_df = stdevs_df.append({'expense_ratio': max_expense_ratio, 'stdev': stdev}, ignore_index=True)

        return (means_df, stdevs_df)


    _, (ax_denominator_bias_0, ax_denominator_bias_1) = plt.subplots(1, 2, sharey=True)
    ax_denominator_bias_0.set_title('Denominator bias 0')
    ax_denominator_bias_0.set_xlabel('Expense ratio')
    ax_denominator_bias_1.set_title('Denominator bias 1')
    ax_denominator_bias_1.set_xlabel('Expense ratio')

    for (ax, denominator_bias) in [(ax_denominator_bias_0, 0), (ax_denominator_bias_1, 1)]:
        means_df, stdevs_df = experiment({'denominator_bias': denominator_bias})
        means_line, = ax.plot(means_df.expense_ratio, means_df['mean'], 'o', color='blue', label='Mean', linestyle='-')
        stdevs_line, = ax.plot(stdevs_df.expense_ratio, stdevs_df.stdev, 'o', color='red', label='StDev', linestyle='-')
        ax.legend(handles=[means_line, stdevs_line])

    plt.savefig(f'plots/biased-expense-ratio-test-{market_type}.png')
    plt.close()
