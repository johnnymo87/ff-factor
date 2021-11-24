import numpy as np
from scipy import optimize

# I want to choose a combination of funds that are both high in factors and
# close to equal as possible in all factors. This idea is similar to the idea
# of the Sharpe ratio, which is the ratio between mean returns and standard
# deviation.
# https://www.kaggle.com/vijipai/lesson-6-sharpe-ratio-based-portfolio-optimization

def choose_best(df):
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
    result = maximize_sharpe_ratio(factor_means, factor_var_covar_matrix)
    if not result.success:
        raise ValueError(result.message)

    df['allocation'] = np.round(result.x, 3)

    chosen = df[(df.allocation > 0)]
    mean = chosen[relevant_columns].\
        agg(lambda x: x.mean(), axis='columns').\
        multiply(chosen.allocation, axis='index').\
        sum().\
        round(3)
    stdev = chosen[relevant_columns].\
        agg(lambda x: x.std(), axis='columns').\
        multiply(chosen.allocation, axis='index').\
        sum().\
        round(3)
    ratio = mean / stdev
    chosen = chosen.append(
        chosen[['mmrf', 'smb', 'hml', 'rmw', 'cma', 'expense_ratio', 'dividend_yield']].\
            multiply(chosen.allocation, axis='index').\
            sum(),
        ignore_index=True
    )

    print(f"Factors considered: {', '.join(relevant_columns)}\n")
    print(f"Mean: {round(mean, 3)}, StDev: {round(stdev, 3)}, Ratio: {round(ratio, 3)}")
    print(f"Choices that best this ratio\n")
    print(chosen.round(3))

    return (mean, stdev, ratio)

def maximize_sharpe_ratio(factor_means, factor_var_covar_matrix):

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
        return -(mean / standard_deviation)

    def equality_constraint(x):
        A = np.ones(x.shape)
        b = 1
        return np.matmul(A, x.T) - b

    # Define bounds and other parameters
    xinit = np.repeat(0.33, len(factor_means))
    constraints = ({'type': 'eq', 'fun': equality_constraint})
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
        tol = 10**-3
    )
