# https://ftp.mcs.anl.gov/pub/tech_reports/reports/P602.pdf
#
# Food            | Cost/Serving | Vitamin A | Calories | Maximum Serving
# Corn (C)        | $0.18        | 107       | 72       | 10
# Milk (M)        | $0.23        | 500       | 121      | 10
# Wheat Bread (W) | $0.05        | 0         | 65       | 10
#
# Nutrient       | Minimum amount in diet | Maximum amount in diet
# Calories (Cal) | 2000                   | 2250
# Vitamin A (VA) | 5000                   | 50000
#
# x[food] = amount of food to eat
# c[food] = cost of 1 serving of food
# A[food] = amount of vitamin A in 1 serving of food
# Cal[food] = amount of calories in 1 serving of food
# MinF[food] = minimum number of servings of food
# MaxF[food] = maximum number of servings of food
# MinN[food] = minimum amount of nutrient required
# MaxN[food] = maximum amount of nutrient required
#
# Solve for x[food]
#
# Minimize              cost[C] * x[C] + cost[M] * x[M] + cost[W] * x[W]
# Subject to MinN[VA]  ≤ A[C] * x[C]   + A[M] * x[M]    + A[W] * x[W]   ≤ MaxN[VA]
#            MinN[Cal] ≤ Cal[C] * x[C] + Cal[M] * x[M]  + Cal[W] * x[W] ≤ MaxN[VA]
#            MinF[C]   ≤                   x[C]                         ≤ MaxF[C]
#            MinF[M]   ≤                   x[M]                         ≤ MaxF[M]
#            MinF[W]   ≤                   x[W]                         ≤ MaxF[W]

# Ticker | cost | mmrf | smb | hml | rmw | cma
# DGRS   | -38  | 91   | 83  | 26  | 34  | 22
# FYT    | -70  | 111  | 99  | 44  | 44  | 0
#
# Factor | Min | Max
# mmrf   | 0   | 111
# smb    | 0   | 100
# hml    | 0   | 100
# rmw    | 0   | 100
# cma    | 0   | 100
#
# qty[ticker] = quantity (percent) to buy of a given investment
# cost[ticker] = cost of 1 percent of a given investment
# mmrf[ticker] = amount of mmrf factor in 1 percent of a given investment
# smb[ticker] = amount of smb factor in 1 percent of a given investment
# hml[ticker] = amount of hml factor in 1 percent of a given investment
# rmw[ticker] = amount of rmw factor in 1 percent of a given investment
# cma[ticker] = amount of cma factor in 1 percent of a given investment
# MinQty[ticker] = minimum quantity (percent) for a given investment
# MaxQty[ticker] = maximum quantity (percent) for a given investment
# MinF[factor] = minimum amount required of factor
# MaxF[factor] = maximum amount required of factor
#
# Solve for qty[ticker]
#
# Minimize                  cost[DGRS] * qty[DGRS] + cost[FYT] * qty[FYT]
# Subject to MinF[mmrf]   ≤ mmrf[DGRS] * qty[DGRS] + mmrf[FYT] * qty[FYT] ≤ MaxF[VA]
#            MinF[smb]    ≤ smb[DGRS] * qty[DGRS] + smb[FYT] * qty[FYT] ≤ MaxF[smb]
#            MinF[hml]    ≤ hml[DGRS] * qty[DGRS] + hml[FYT] * qty[FYT] ≤ MaxF[hml]
#            MinF[rmw]    ≤ rmw[DGRS] * qty[DGRS] + rmw[FYT] * qty[FYT] ≤ MaxF[rmw]
#            MinF[cma]    ≤ cma[DGRS] * qty[DGRS] + cma[FYT] * qty[FYT] ≤ MaxF[cma]
#            MinQty[DGRS] ≤                   qty[DGRS]                 ≤ MaxQty[DGRS]
#            MinQty[FYT]  ≤                   qty[FYT]                  ≤ MaxQty[FYT]

# https://developers.google.com/optimization/lp/glop#python_data
import pandas as pd
from ortools.algorithms import pywrapknapsack_solver

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
    # investments = investments[['ticker', 'expense_ratio', 'dividend_yield']]
    # investments.expense_ratio = investments.expense_ratio.transform(lambda x: -x)
    # investments.dividend_yield = investments.dividend_yield.transform(lambda x: -x)
    # df = pd.merge(factors, investments, on='ticker')
    df = factors
    df = df.reset_index()
    df = df.sort_values(by=['ticker'], ascending=False)

    columns = df.columns.drop('ticker') # factors only

    # Available solvers:
    # KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER
    # KNAPSACK_MULTIDIMENSION_CBC_MIP_SOLVER
    # KNAPSACK_MULTIDIMENSION_SCIP_MIP_SOLVER
    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.
        KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'FFFactorKnapsackSolver')


    # data frame with normalized factor exposures
    # ndf = df.copy(deep=True)
    # ndf.iloc[:, 1:] = ndf.iloc[:, 1:].apply(lambda x: (x - x.mean()) / x.std(), axis=0)

    sums = df[columns].sum(axis=1) # sum of all factors for each ticker
    maxs = df[columns].max()       # max of each type of factor

    # data frame of "max minus my" exposures, to capture opportunity cost
    cdf = df.copy(deep=True)
    cdf.iloc[:, 1:] = cdf.iloc[:, 1:].apply(lambda x: x.max() - x, axis=0)

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
