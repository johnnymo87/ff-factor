from lib.chosen_summarizer import ChosenSummarizer
import numpy as np
from scipy import optimize

# I want to choose a combination of funds that are both high in factors and
# close to equal as possible in all factors. This idea is similar to the idea
# of the Sharpe ratio, which is the ratio between mean returns and standard
# deviation.
# https://www.kaggle.com/vijipai/lesson-6-sharpe-ratio-based-portfolio-optimization

def choose_best(df, weights_and_biases={}):
    if df.shape[0] <= 1:
        print(f'DataFrame is too small ({df.shape[0]}), skipping')
        return (0, 0, 0)

    relevant_columns = ['smb', 'hml', 'rmw', 'cma']
    if len(set(df.columns) & set(relevant_columns)) != len(relevant_columns):
        raise ValueError(f'DataFrame columns ({",".join(df.columns)}) does not contain all relevant columns ({",".join(relevant_columns)})')

    # Compute the mean and variance-covariance matrix
    factors = np.asarray(df[relevant_columns])
    factor_means = np.mean(factors, axis = 1)
    # https://numpy.org/doc/stable/reference/generated/numpy.cov.html
    # Bias true because I don't want to exclude one of my "observations" (factors)
    factor_var_covar_matrix = np.cov(factors, bias=True)

    # Compute maximal Sharpe Ratio and optimal weights
    result = maximize_sharpe_ratio(factor_means, factor_var_covar_matrix, weights_and_biases)
    if not result.success:
        raise ValueError(result.message)

    df['allocation'] = np.round(result.x, 3)

    chosen = df[(df.allocation > 0)].sort_values(by=['allocation'], ascending=False)
    # mean = chosen[relevant_columns].\
    #     multiply(chosen.allocation, axis='index').\
    #     sum().\
    #     mean().\
    #     round(3)
    # stdev = chosen[relevant_columns].\
    #     multiply(chosen.allocation, axis='index').\
    #     sum().\
    #     std().\
    #     round(3)
    # ratio = mean / stdev
    # chosen = chosen.append(
    #     chosen[['mmrf', 'smb', 'hml', 'rmw', 'cma', 'expense_ratio', 'dividend_yield']].\
    #         multiply(chosen.allocation, axis='index').\
    #         sum(),
    #     ignore_index=True
    # )

    # print(f"Factors considered: {', '.join(relevant_columns)}\n")
    # print(f"Mean: {round(mean, 3)}, StDev: {round(stdev, 3)}, Ratio: {round(ratio, 3)}")
    # print(f"Choices that best this ratio\n")
    # print(chosen.round(3))

    # return (mean, stdev, ratio, chosen)
    return ChosenSummarizer(chosen, relevant_columns)

def maximize_sharpe_ratio(factor_means, factor_var_covar_matrix, weights_and_biases):
    numerator_weight = weights_and_biases.get('numerator_weight', 1)
    numerator_bias = weights_and_biases.get('numerator_bias', 0)
    denominator_weight = weights_and_biases.get('denominator_weight', 1)
    denominator_bias = weights_and_biases.get('denominator_bias', 0)

    def objective_function(x, given_factor_means, given_factor_var_covar_matrix):
        standard_deviation = np.sqrt(
            np.matmul(
                np.matmul(x, given_factor_var_covar_matrix),
                x.T
            )
        )
        mean = np.matmul(np.array(given_factor_means), x.T)
        # Since the optimizer minimizes and we want to maximize, we negate our
        # objective function.
        return -(numerator_bias + numerator_weight * mean) / (denominator_bias + denominator_weight * standard_deviation)

    # Enforce that all allocations sum to 1
    def equality_constraint(x):
        A = np.ones(x.shape)
        b = 1
        return np.matmul(A, x.T) - b
    constraints = ({'type': 'eq', 'fun': equality_constraint})

    # Enforce that all allocations are positive
    xinit = np.repeat(0.33, len(factor_means))
    lower_bound = 0
    upper_bound = 1
    bounds = tuple([(lower_bound, upper_bound) for x in xinit])

    # Invoke minimize solver
    return optimize.minimize(
        objective_function,
        x0 = xinit,
        args = (
            factor_means,
            factor_var_covar_matrix
        ),
        method = 'SLSQP',
        bounds = bounds,
        constraints = constraints,
        # https://stackoverflow.com/questions/11155721/positive-directional-derivative-for-linesearch
        # https://stackoverflow.com/questions/9667514/what-is-the-difference-between-xtol-and-ftol-to-use-fmin-of-scipy-optimize
        tol = 10**-2
    )
