from itertools import permutations
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn import preprocessing

def optimize(factors, investments):
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
    investments = investments[['ticker', 'expense_ratio', 'dividend_yield']]
    # df = pd.merge(factors, investments, on='ticker')
    df = factors
    df = df.reset_index()
    df = df.sort_values(by=['ticker'], ascending=False)
    df = df.merge(investments, on='ticker')

    EXPENSE_RATIO_MAX = 0.4
    SMB_MAX, HML_MAX, RMW_MAX, CMA_MAX = 1, 0.55, 0.6, 0.22
    # df = df[(df.expense_ratio <= EXPENSE_RATIO_MAX)]


    factor_columns = list(set(df.columns) & set(renamed.values()))



    # data frame with normalized factor exposures
    # ndf = df.copy(deep=True)
    # ndf.iloc[:, 1:] = ndf.iloc[:, 1:].apply(lambda x: (x - x.mean()) / x.std(), axis=0)

    # profits = df[factor_columns].sum(axis=1) # sum of all factors for each ticker
    # maxs = df[factor_columns].max()       # max of each type of factor

    # data frame of "max minus my" exposures, to capture opportunity cost
    # cdf = df.copy(deep=True)
    # cdf.loc[:, factor_columns] = cdf.loc[:, factor_columns].apply(lambda x: x.max() - x, axis=0)
    # costs = cdf[factor_columns].sum(axis=1)
    # df['profit'] = profits
    # df['cost'] = costs
    # df['efficiency'] = sums.div(df.expense_ratio)

    # normalize the factor columns on a scale of 0 to 1
    min_max_scaler = preprocessing.MinMaxScaler()
    pd.DataFrame(min_max_scaler.fit_transform(df[factor_columns]), columns=factor_columns, index=df.index)

    df['profit'] = df[factor_columns].sum(axis=1) # sum of all factors for each ticker
    df['efficiency'] = df.profit.div(df.expense_ratio)
    df['stddev'] = df[factor_columns].std(axis=1)

    for left, right in permutations(factor_columns, 2):
        fig = sns.lmplot(x=left, y=right, data=df[[left, right]], fit_reg=True)
        plt.savefig(f'plots/{left}-{right}.png')
        plt.close()

    fig = sns.lmplot(x='expense_ratio', y='profit', data=df[['expense_ratio', 'profit']], fit_reg=True)
    plt.savefig(f'plots/cost_efficiency.png')
    plt.close()

    fig = sns.lmplot(x='stddev', y='profit', data=df[['stddev', 'profit']], fit_reg=True)
    plt.savefig(f'plots/stddev-profit.png')
    plt.close()

    opportunity_costs = df.loc[:, factor_columns].apply(lambda x: x.max() - x, axis=0)
    # sac = df[['ticker']].join(opportunity_costs.sum(axis=1).rename('factor_sacrifice')).merge(investments, on='ticker')

    for factor_column in factor_columns:
        # fig = sns.lmplot(x=factor_column, y='expense_ratio', data=df, fit_reg=True)
        # plt.savefig(f'plots/{factor_column}_cost_efficiency.png')
        # plt.close()

        other_factor_columns = (set(factor_columns) - set(factor_column))
        sacrifice = opportunity_costs[other_factor_columns].sum(axis=1).rename('sacrifice')
        fig = sns.lmplot(x=factor_column, y='sacrifice', data=df.join(sacrifice), fit_reg=True)
        plt.savefig(f'plots/{factor_column}-sacrifice.png')
        plt.close()

        # Efficiency: High score means it sacrifices other factors LESS
        # df[f'{factor_column}_eff'] = df[factor_column].div(sacrifice)

    import pdb; pdb.set_trace()
    # for factor_column in factor_columns:
    #     for other_factor_column in (set(factor_columns) - set(factor_column)):
    #         df[f'{other_factor_column}_opportunity_cost'] = maxs.minus(df[other_factor_column])

        # df[f'{factor_column}_opportunity_cost'] = maxs.minus(df[factor_column])
        # cdf.loc[:, factor_columns] = cdf.loc[:, factor_columns].apply(lambda x: x.max() - x, axis=0)
        # per factor
        # sum of opportunity cost of each of the other factors
        # df[f'{factor_column}_cost'] = cdf.profit.minus(cdf[factor_column])
    # cdf.loc[:, columns] = cdf.loc[:, columns].apply(lambda x: 0 if x == 0 else x.profit / x, axis=0)

    # rename variables to match code example
    values = sums.values.tolist()
    weights = [cdf[column].values.tolist() for column in columns]
    capacities = maxs.mul(100).values.tolist()

    values = [int(x * 100) for x in values]
    weights = [[int(x * 100) for x in xs] for xs in weights]
    capacities = [int(x * 100) for x in capacities]

    # solve
    solver.Init(values, weights, capacities)
    computed_value = solver.Solve()
    optimal_tickers = [df.iloc[i].ticker for i in range(len(values)) if solver.BestSolutionContains(i)]


    import pdb; pdb.set_trace()

    # Each possible investment is a variable
    ticker_variables = [solver.NumVar(0, solver.infinity(), row.ticker) for _, row in df.iterrows()]
    # Each factor is a variable
    factor_variables = [solver.NumVar(0, solver.infinity(), column) for column in columns]

    constraints = []

    # constraint 1: 100 ≤ sum of all investments ≤ 100
    constraint = solver.Constraint(100, 100, 'sum')
    for ticker_variable in ticker_variables:
        constraint.SetCoefficient(ticker_variable, 1)
    constraints.append(constraint)

    # data frame with normalized factor exposures
    ndf = df.copy(deep=True)
    ndf.iloc[:, 1:] = ndf.iloc[:, 1:].apply(lambda x: (x - x.mean()) / x.std(), axis=0)

    # constraint with ticker variables: min[factor] * 100 ≤ sum of all investment's exposure to factor ≤ max[factor] * 100
    mins = ndf[columns].min().mul(100)
    maxs = ndf[columns].max().mul(100)
    for column in columns:
        constraint = solver.Constraint(mins[column], maxs[column], column)
        constraints.append(constraint)
        for i, row in ndf.iterrows():
            constraint.SetCoefficient(ticker_variables[i], row[column])

    # constraint with factor variables: min[factor] * 100 ≤ sum of all investment's exposure to factor ≤ max[factor] * 100
    for i, column in enumerate(columns):
        constraint = solver.Constraint(mins[column], maxs[column], column)
        constraints.append(constraint)
        _sum = sum(row[column] for _, row in ndf.iterrows())
        constraint.SetCoefficient(factor_variables[i], _sum)

    # Objective: maximize the exposure to all factors equally
    objective = solver.Objective()
    for i, column in enumerate(columns):
        objective.SetCoefficient(factor_variables[i], maxs[column])
        # objective.SetCoefficient(factor_variables[i], 1)
    objective.SetMaximization()

    # Solve!
    status = solver.Solve()

    dual_values = { constraint.name(): constraint.dual_value() for constraint in constraints }
    print('Dual values')
    print(dual_values)

    if status == solver.OPTIMAL:
        print('The solver found an optimal solution')
    elif status == solver.FEASIBLE:
        print('The solver found a potentially suboptimal solution')
    else:
        print('The solver could not solve the problem')
        import pdb; pdb.set_trace()

    solutions = { str(variable): variable.solution_value() for variable in ticker_variables if variable.solution_value() > 0 }
    # total = sum(solutions.values())
    # percentages = { ticker: solution / total for ticker, solution in solutions.items() }

    sf = df[df.ticker.isin(solutions.keys())].loc[:]
    print('Chosen investments')
    print(sf.round(2))

    print('Percent allocation by investment')
    print({ ticker: round(percent, 1) for ticker, percent in solutions.items() })

    for ticker, percent in solutions.items():
        sf.loc[sf.ticker == ticker, columns] =\
            sf.loc[sf.ticker == ticker, columns].\
            apply(lambda x: x * percent / 100)
    print('Factor exposure')
    print(sf[columns].sum().round(2))

    import pareto
    df_pareto = pd.DataFrame.from_records(pareto.eps_sort([*df[columns].itertuples(index=False)]), columns=columns.values)
    import pdb; pdb.set_trace()
