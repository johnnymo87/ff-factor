from lib.factor_returns import FactorReturns
from lib.investment_returns import InvestmentReturns
from lib.investments import Investments
# Pandas to read csv file and other things
import pandas as pd
# To prepare design matrices using R-like formulas
from patsy import dmatrices
# Statsmodels to run our multiple regression model
import statsmodels.api as sm

from lib.sharpe_ratio_solver import choose_best

FIVE_FACTOR_FORMULA = """
port_excess ~ market_minus_risk_free + small_minus_big + high_minus_low + robust_minus_weak + conservative_minus_aggressive
"""

if __name__ == '__main__':
    market_type = 'US'
    # market_type = 'Developed ex US'
    # market_type = 'Emerging'

    # Get the French-Fama Data
    ff_data = FactorReturns.fetch(market_type)
    ff_starts_at = ff_data.occurred_at.min()
    ff_ends_at = ff_data.occurred_at.max()

    # Get the investments to study
    # Investments().backfill_facts(market_type)
    investments = Investments().query.for_analysis(market_type, ff_ends_at)

    results = {}
    for investment in investments:
        ticker_symbol = investment.ticker_symbol
        # print(f'Analyzing {ticker_symbol}')
        try:
            # Get the returns of the investment
            ticker_data = InvestmentReturns.fetch(ticker_symbol, ff_starts_at, ff_ends_at)
            if len(ticker_data) < 12:
                print(f'Less than 12 months of data, skipping {ticker_symbol}!')
                continue

            # Join the FF and investment returns data
            all_data = pd.merge(ticker_data, ff_data, on='occurred_at')
            all_data['port_excess'] = all_data.percentage_change - all_data.risk_free

            # Run OLS regression
            endogenous, exogenous = dmatrices(FIVE_FACTOR_FORMULA, data=all_data, return_type='dataframe')
            results[ticker_symbol] = sm.OLS(endogenous, exogenous).fit()

        except KeyError as e:
            print(f'Skipping {ticker_symbol} due to lack of Yahoo API response')

    dfs = []
    for ticker, result in results.items():
        df = pd.DataFrame({ 'coef': result.params, 'tvalue': result.tvalues, 'pvalue': result.pvalues })
        df['factor'] = df.index
        df['ticker'] = ticker
        df.set_index(['ticker'])
        dfs.append(df)

    df = pd.concat(dfs)
    # df = pd.merge(df, investments.to_data_frame(), on='ticker')

    # Remove inverse funds
    inversed = df[(df.coef <= 0) & (df.factor == 'market_minus_risk_free')]
    df = df[~df.ticker.isin(inversed.ticker)]
    # Remove leveraged funds
    leveraged = df[(df.coef >= 2) & (df.factor == 'market_minus_risk_free')]
    df = df[~df.ticker.isin(leveraged.ticker)]
    # Exclude 'Intercept' because it almost always very close to zero
    df = df[~df.factor.isin(['Intercept'])]
    # Exclude 'market_minus_risk_free' because it usually close to one
    # df = df[~df.factor.isin(['market_minus_risk_free'])]

    # Exclude statistically insignificant results
    df = df[df.pvalue <= 0.05]

    renamed = {
        'market_minus_risk_free': 'mmrf',
        'small_minus_big': 'smb',
        'high_minus_low': 'hml',
        'robust_minus_weak': 'rmw',
        'conservative_minus_aggressive': 'cma'}
    df = df[['ticker', 'factor', 'coef']].\
        pivot(index='ticker', columns='factor', values='coef').\
        rename(columns=renamed)
    df = df.reset_index() # Make index integers rather than ticker

    investments_df = investments.to_data_frame()[['ticker', 'expense_ratio', 'dividend_yield']]
    # Throw out funds missing their expense ratio
    investments_df = investments_df[investments_df.expense_ratio.notna()]
    # Throw out funds that are too expensive
    investments_df = investments_df[(investments_df.expense_ratio <= 0.4)]

    df = df.merge(investments_df, on='ticker')

    # Replacing all NaNs with zero. This isn't perfect because:
    # * Factors with just barely insignificant p-values will be zero, when in
    #   fact they might be negative.
    # * Dividend yield that are missing in the API will appear as zero.
    df = df.fillna(0)

    # print('Consider catching a debugger here to play with the data frames')
    # print('Write "import pdb; pdb.set_trace()" and run "python ."')
    # print(df.head())

    choose_best(df)
