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
        chosen_summarizer = choose_best(df.sample(frac=0.8), weights_and_biases={'denominator_bias': 1})
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
        # print(results_df[results_df.index == i])
        print(chosen_summarizers[i].summary())
        # chosen = chosen.append(
        #     chosen_summarizer.summarize(relevant_columns=['mmrf', 'smb', 'hml', 'rmw', 'cma', 'expense_ratio', 'dividend_yield']),
        #     ignore_index=True
        # )
        # print(chosen.round(3))
        print()

    # print(f"Factors considered: {', '.join(relevant_columns)}\n")
    # print(f"Mean: {round(mean, 3)}, StDev: {round(stdev, 3)}, Ratio: {round(ratio, 3)}")
    # print(f"Choices that best this ratio\n")
    # print(chosen.round(3))

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
