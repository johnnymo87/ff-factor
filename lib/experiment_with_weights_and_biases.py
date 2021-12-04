
from lib.sharpe_ratio_solver import choose_best
import pandas as pd
import matplotlib.pyplot as plt

# I don't think it makes sense to have the solver consider expense ratio and
# dividend yield when solving for factors. So as an alternative, I'll walk down
# the curve where I trade off expense ratio for results. I'll plot this and
# look for any cliffs or plateaus.
MAX_EXPENSE_RATIO = 0.5

def experiment_with_weights_and_biases(df, market_type):
    df_this_experiment = df.copy(deep=True).loc[df.expense_ratio <= MAX_EXPENSE_RATIO]
    print(f"\n\nCalculating the best score for {df_this_experiment.shape[0]} funds where the max expense ratio is {MAX_EXPENSE_RATIO}\n\n")

    def experiment(weights_and_biases):
        means_df = pd.DataFrame()
        stdevs_df = pd.DataFrame()

        for denominator_weight in range(1, 11):
            weights_and_biases['denominator_weight'] = denominator_weight
            print(f"\n\nCalculating the best score when weights and biases are {weights_and_biases}")
            (mean, stdev, _) = choose_best(df_this_experiment, weights_and_biases=weights_and_biases)
            means_df = means_df.append({'denominator_weight': denominator_weight, 'mean': mean}, ignore_index=True)
            stdevs_df = stdevs_df.append({'denominator_weight': denominator_weight, 'stdev': stdev}, ignore_index=True)

        return (means_df, stdevs_df)

    _, (ax_denominator_bias_0, ax_denominator_bias_1) = plt.subplots(1, 2, sharey=True)
    ax_denominator_bias_0.set_title('Denominator bias 0')
    ax_denominator_bias_0.set_xlabel('denominator weight')
    ax_denominator_bias_1.set_title('Denominator bias 1')
    ax_denominator_bias_1.set_xlabel('denominator weight')

    for (ax, denominator_bias) in [(ax_denominator_bias_0, 0), (ax_denominator_bias_1, 1)]:
        means_df, stdevs_df = experiment({'denominator_bias': denominator_bias})
        means_line, = ax.plot(means_df.denominator_weight, means_df['mean'], 'o', color='blue', label='Mean', linestyle='-')
        stdevs_line, = ax.plot(stdevs_df.denominator_weight, stdevs_df.stdev, 'o', color='red', label='StDev', linestyle='-')
        ax.legend(handles=[means_line, stdevs_line])

    plt.savefig(f'plots/weights-and-biases-test-{market_type}.png')
    plt.close()

# def experiment_with_weights_and_biases(df, market_type):
#     df_this_experiment = df.copy(deep=True).loc[df.expense_ratio <= MAX_EXPENSE_RATIO]
#     print(f"\n\nCalculating the best score for {df_this_experiment.shape[0]} funds where the max expense ratio is {MAX_EXPENSE_RATIO}\n\n")
#
#     _, ax = plt.subplots()
#     means_df = pd.DataFrame()
#     stdevs_df = pd.DataFrame()
#
#     for denominator_weight in range(0, 10):
#         weights_and_biases_this_run = {'denominator_bias': 1, 'denominator_weight': denominator_weight}
#         print(f"\n\nCalculating the best score when weights and biases are {weights_and_biases_this_run}")
#         (mean, stdev, _) = choose_best(df_this_experiment, weights_and_biases=weights_and_biases_this_run)
#         means_df = means_df.append({'denominator_weight': denominator_weight, 'mean': mean}, ignore_index=True)
#         stdevs_df = stdevs_df.append({'denominator_weight': denominator_weight, 'stdev': stdev}, ignore_index=True)
#
#     ax.set_xlabel('denominator weight')
#     means_line, = ax.plot(means_df.denominator_weight, means_df['mean'], 'o', color='blue', label='Mean', linestyle='-')
#     stdevs_line, = ax.plot(stdevs_df.denominator_weight, stdevs_df.stdev, 'o', color='red', label='StDev', linestyle='-')
#     ax.legend(handles=[means_line, stdevs_line])
#
#     plt.savefig(f'plots/weights-and-biases-test-{market_type}.png')
#     plt.close()

# def experiment_with_weights_and_biases(df, market_type):
#     df_this_experiment = df.copy(deep=True).loc[df.expense_ratio <= MAX_EXPENSE_RATIO]
#     print(f"\n\nCalculating the best score for {df_this_experiment.shape[0]} funds where the max expense ratio is {MAX_EXPENSE_RATIO}\n\n")
#
#     def experiment(ax, variable_name, variables):
#         means_df = pd.DataFrame()
#         stdevs_df = pd.DataFrame()
#
#         for variable in variables:
#             weights_and_biases_this_run = {variable_name: variable}
#             print(f"\n\nCalculating the best score when weights and biases are {weights_and_biases_this_run}")
#             (mean, stdev, _) = choose_best(df_this_experiment, weights_and_biases=weights_and_biases_this_run)
#             means_df = means_df.append({variable_name: variable, 'mean': mean}, ignore_index=True)
#             stdevs_df = stdevs_df.append({variable_name: variable, 'stdev': stdev}, ignore_index=True)
#
#         ax.set_xlabel(variable_name)
#         means_line, = ax.plot(means_df[variable_name], means_df['mean'], 'o', color='blue', label='Mean', linestyle='-')
#         stdevs_line, = ax.plot(stdevs_df[variable_name], stdevs_df.stdev, 'o', color='red', label='StDev', linestyle='-')
#         ax.legend(handles=[means_line, stdevs_line])
#
#     _, ((ax_numerator_weight, ax_numerator_bias), (ax_denominator_weight, ax_denominator_bias)) = plt.subplots(2, 2, sharex=True, sharey=True)
#     experiment(ax_numerator_weight, 'numerator_weight', [1, 2, 3, 4, 5])
#     experiment(ax_numerator_bias, 'numerator_bias', [0, 1, 2, 3, 4])
#     experiment(ax_denominator_weight, 'denominator_weight', [1, 2, 3, 4, 5])
#     experiment(ax_denominator_bias, 'denominator_bias', [0, 1, 2, 3, 4])
#
#     plt.savefig(f'plots/weights-and-biases-test-{market_type}.png')
#     plt.close()
