# To find the last day of the month
import calendar
# To parse the CSV
import csv
# To convert the 'occurred_at' values
import datetime
# To help merging data frames
import functools
# To do some conversions and to merge data frames
import pandas as pd
# To download the Fama French data from the web
import urllib.request
# To unzip the downloaded zip file
import zipfile

# To check if a file exists
from os import path

class FactorReturnsDownloader:
    class BaseDataSource:
        def __init__(self, market_type, filename):
            self.__market_type = market_type
            self.__filename = filename

        def market_type(self):
            return self.__market_type

        def set_csv_filename(self, given_filename):
            self.__csv_filename = given_filename

        def csv_filename(self):
            return f'downloads/{self.__csv_filename}'

        def url(self):
            return f'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{self.__filename}_CSV.zip'

        def zip_filename(self):
            return f'downloads/{self.__filename}_CSV.zip'

        DATE_FORMAT = '%Y%m'

        @classmethod
        def parse_date(self, given_date):
            d = datetime.datetime.strptime(given_date.strip(), self.DATE_FORMAT).date()
            return datetime.date(d.year, d.month, calendar.monthrange(d.year, d.month)[-1])

        MISSING = -99.99

        @classmethod
        def parse_float(self, given_float):
            f = float(given_float)
            return None if f == self.MISSING else f / 100

        def parse(self, given_row):
            if not len(given_row) == len(self.columns()):
                return
            try:
                head, *tail = given_row
                return [self.parse_date(head)] + [self.parse_float(el) for el in tail]
            except ValueError:
                return


    class FiveFactorDataSource(BaseDataSource):
        def __init__(self, market_type, filename):
            self.__columns = [
                'occurred_at',
                'market_minus_risk_free',
                'small_minus_big',
                'high_minus_low',
                'robust_minus_weak',
                'conservative_minus_aggressive',
                'risk_free'
            ]
            super().__init__(market_type, filename)

        def columns(self):
            return self.__columns

    class MomentumFactorDataSource(BaseDataSource):
        def __init__(self, market_type, filename):
            self.__columns = ['occurred_at', 'winners_minus_losers']
            super().__init__(market_type, filename)

        def columns(self):
            return self.__columns

    DATA_SOURCES = [
        FiveFactorDataSource('Emerging', 'Emerging_5_Factors'),
        MomentumFactorDataSource('Emerging', 'Emerging_MOM_Factor'),
        FiveFactorDataSource('Developed ex US', 'Developed_ex_US_5_Factors'),
        MomentumFactorDataSource('Developed ex US', 'Developed_ex_US_Mom_Factor'),
        FiveFactorDataSource('US', 'F-F_Research_Data_5_Factors_2x3'),
        MomentumFactorDataSource('US', 'F-F_Momentum_Factor')
    ]

    @staticmethod
    def download_all():
        """
        @raise [???] If file can't be found
        @raise [???] If the file isn't a CSV
        @return [dict] For each pair, the key is a [string], and the value is a [pandas.core.frame.DataFrame]
        """
        result = {}
        for data_source in FactorReturnsDownloader.DATA_SOURCES:
            result.setdefault(data_source.market_type(), [])
            data_frame = FactorReturnsDownloader(data_source).to_data_frame()
            result[data_source.market_type()].append(data_frame)
        for key, data_frames in result.items():
            result[key] = functools.reduce(lambda a, b: pd.merge(a, b, on='occurred_at'), data_frames)
        return result

    def __init__(self, data_source):
        self.data_source = data_source

    def to_data_frame(self):
        """
        @raise [FileNotFoundError] If file can't be found
        @raise [???] If the file isn't a zipfile
        @raise [???] If the file isn't a CSV
        @return [pandas.core.frame.DataFrame]
        """
        self.download_zipfile()
        self.extract_zipfile()
        return self.from_csv()

    def download_zipfile(self):
        """
        @param [string] Filename of the zip file without the suffix nor the extension, e.g. Emerging_5_Factors
        @raise [FileNotFoundError] If downloads directory doesn't exist
        @raise [urllib.error.URLError] If file can't be downloaded
        @return [None]
        """
        if path.isfile(self.data_source.zip_filename()):
            return

        urllib.request.urlretrieve(self.data_source.url(), self.data_source.zip_filename())

    def extract_zipfile(self):
        """
        @raise [FileNotFoundError] If file can't be found
        @raise [???] If the file isn't a zip file
        @return [None]
        """
        with zipfile.ZipFile(self.data_source.zip_filename(), 'r') as z:
            # Capture CSV's filename, as it varies slightly and thus cannot be arrived at programmatically
            self.data_source.set_csv_filename(z.namelist()[0])

            if path.isfile(self.data_source.csv_filename()):
                return

            z.extractall('downloads')

    def from_csv(self):
        """
        @raise [FileNotFoundError] If file can't be found
        @raise [???] If the file isn't a CSV
        @return [pandas.core.frame.DataFrame] A cleaned-up data frame, parsed from the CSV
        """
        with open(self.data_source.csv_filename(), 'r') as input_file:
            rows = [self.data_source.parse(row) for row in csv.reader(input_file)]
            rows = [row for row in rows if row]
            return pd.DataFrame(rows, columns=self.data_source.columns())
