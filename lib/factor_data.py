from db.db import Session
from db.factor import Factor
from db.source_filename import SourceFilename
# Pandas to read sql and csv files, and do some conversions
import pandas as pd
# To download the Fama French data from the web
import urllib.request
# To unzip the downloaded zip file
import zipfile

class FactorData:
    URL = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'

    @staticmethod
    def download_zipfile(filename):
        """
        @param [string] Final bit of URL specifying the name of the zip file, e.g. Emerging_5_Factors_CSV.zip
        @raise [???] If file can't be downloaded
        """
        urllib.request.urlretrieve(f'{URL}{filename}', f'downloads/{filename}')

    @staticmethod
    def extract_zipfile(filename):
        """
        @param [string] Filename of the zip file, e.g. Emerging_5_Factors_CSV.zip
        @raise [???] If file can't be found
        @raise [???] If the file isn't a zip file
        @return [string] The filename of the CSV inside the zip
        """
        with zipfile.ZipFile(f'downloads/{filename}', 'r') as z:
            z.extractall()
            # Look up CSV's filename, as it may differ slightly
            return z.namelist()[0]

    @staticmethod
    def parse_csv(filename):
        """
        @param [string] Filename of the CSV, e.g. Emerging_5_Factors.csv
        @raise [???] If file can't be found
        @raise [???] If the file isn't a CSV
        @return [pandas.core.frame.DataFrame] A cleaned-up dataframe, parsed from the CSV
        """
        # All CSVs from this site have a 3-row header that we skip
        ff_factors = pd.read_csv(f'downloads/{filename}', skiprows=3, index_col=0)

        # We want to find out the row with NULL values and skip them
        null_rows = ff_factors.isnull().any(1).to_numpy().nonzero()[0][0]
        ff_factors = pd.read_csv(f'downloads/{filename}', skiprows=3, nrows=null_rows, index_col=0)

        # Format the date index
        ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m')

        # Format dates to end of month
        ff_factors.index = ff_factors.index + pd.offsets.MonthEnd()

        # Convert from percent to decimal
        ff_factors = ff_factors.apply(lambda x: x/ 100)

        # Adjust all column names to be downcased and underscored
        ff_factors = ff_factors.rename(columns=lambda x: x.replace('-', '_').lower())

        # Clone the index (date) column to a regular column so that we can:
        # * write it to the db
        # * access it like a regular column
        ff_factors['occurred_at'] = ff_factors.index

        return ff_factors

    @staticmethod
    def fetch(filename):
        """
        @param [string] Filename of the CSV, e.g. Emerging_5_Factors.csv
        @raise [???] If file can't be found
        @raise [???] If the file isn't a CSV
        @return [pandas.core.frame.DataFrame]
        """
        session = Session()
        source_filename = session.query(SourceFilename).filter(SourceFilename.filename == filename).one_or_none()
        if source_filename is None:
            print(f'Factor data for {filename} not found in the DB, backfilling it from the CSV')
            ff_data = FactorData.parse_csv(filename)
            source_filename = SourceFilename(filename=filename)
            session.add(source_filename)
            session.flush()
            ff_data['source_filename_id'] = source_filename.id
            session.add_all([Factor(**row) for _, row in ff_data.iterrows()])
            session.commit()
        query = session.query(Factor).filter(Factor.source_filename_id == source_filename.id)
        return pd.read_sql(query.statement, query.session.bind)
