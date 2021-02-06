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
from ortools.linear_solver import pywraplp

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

    # Instantiate a Glop solver, naming it SolveStigler in honor of the original problem
    solver = pywraplp.Solver('SolveStigler', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    # Objective: maximize the exposure to factors for minimal price
    objective = solver.Objective()
    variables = [[]] * len(df)
    for i, row in df.iterrows():
        variables[i] = solver.NumVar(0, solver.infinity(), row.ticker)
        objective.SetCoefficient(variables[i], 1)
    objective.SetMaximization()

    columns = df.columns.drop('ticker')
    constraints = [0] * len(columns)
    for i, column in enumerate(columns):
        # _min = 0
        _min = min(df[column])
        _max = max(df[column])
        # print(f'{column} min: {round(_min, 2)} max: {round(_max, 2)}')
        constraints[i] = solver.Constraint(_min, _max, column)
        for j, row in df.iterrows():
            # print(f'{variables[j]} coef {round(row[column], 2)}')
            constraints[i].SetCoefficient(variables[j], row[column])

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

    solutions = { str(variable): variable.solution_value() for variable in variables if variable.solution_value() > 0 }
    total = sum(solutions.values())
    percentages = { ticker: solution / total for ticker, solution in solutions.items() }

    sf = df[df.ticker.isin(percentages.keys())].loc[:]
    print('Chosen investments')
    print(sf.round(2))

    print('Percent allocation by investment')
    print({ ticker: round(percent * 100, 1) for ticker, percent in percentages.items() })

    for ticker, percent in percentages.items():
        sf.loc[sf.ticker == ticker, columns] =\
            sf.loc[sf.ticker == ticker, columns].\
            apply(lambda x: x * percent)
    print('Factor exposure')
    print(sf[columns].sum().round(2))

    import pdb; pdb.set_trace()
