# I want to choose a combination of funds that are both high in factors and
# close to equal as possible in all factors. This idea is similar to the idea
# of the Sharpe ratio, which is the ratio between mean returns and standard
# deviation.
# https://www.kaggle.com/vijipai/lesson-6-sharpe-ratio-based-portfolio-optimization

import numpy as np
from scipy import optimize

def choose_best(factors, investments):
    renamed = {
        'market_minus_risk_free': 'mmrf',
        'small_minus_big': 'smb',
        'high_minus_low': 'hml',
        'robust_minus_weak': 'rmw',
        'conservative_minus_aggressive': 'cma'}
    factors = factors[['ticker', 'factor', 'coef']].\
        pivot(index='ticker', columns='factor', values='coef').\
        rename(columns=renamed).\
        fillna(0)
    other_columns = ['ticker', 'expense_ratio', 'dividend_yield']
    investments = investments[other_columns]
    # df = pd.merge(factors, investments, on='ticker')
    df = factors
    df = df.reset_index()
    df = df.sort_values(by=['ticker'], ascending=False)
    df = df.merge(investments, on='ticker')

    EXPENSE_RATIO_MAX = 0.4
    df = df[(df.expense_ratio <= EXPENSE_RATIO_MAX)]

    factor_columns = list(set(df.columns) & set(renamed.values()))

    # Compute the mean and variance-covariance matrix
    factors = np.asarray(df[factor_columns])
    factor_means = np.mean(factors, axis = 1)
    # https://numpy.org/doc/stable/reference/generated/numpy.cov.html
    # Bias true because I don't want to exclude one of my "observations" (factors)
    factor_var_covar_matrix = np.cov(factors, bias=True)

    # Compute maximal Sharpe Ratio and optimal weights
    result = maximize_sharpe_ratio(factor_means, factor_var_covar_matrix)

    df['allocation'] = np.round(result.x, 3)
    chosen = df[(df.allocation > 0)]
    print("\nBest ratio of total factor value to minimum factor variance:\n")
    print(chosen)

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
