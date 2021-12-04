import numpy as np

class ChosenSummarizer:
    def __init__(self, chosen, relevant_columns):
        self.chosen = chosen
        self.relevant_columns = relevant_columns

    def summary(self):
        print({
            'mean': self.mean().round(3),
            'stdev': self.stdev().round(3),
            'sharpe_ratio': self.sharpe_ratio().round(3)
        })
        print(
            self.chosen.append(
                self.summarize(relevant_columns=['mmrf', 'smb', 'hml', 'rmw', 'cma', 'expense_ratio', 'dividend_yield']),
                ignore_index=True
            ).round(3)
        )

    def summarize(self, relevant_columns=None):
        return self.chosen[relevant_columns or self.relevant_columns].\
            multiply(self.chosen.allocation, axis='index').\
            sum()

    def mean(self):
        return self.summarize().mean()

    def stdev(self):
        return self.summarize().std()

    def sharpe_ratio(self):
        return self.mean() / self.stdev()
