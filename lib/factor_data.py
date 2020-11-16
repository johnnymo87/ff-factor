from db.source_filename import SourceFilename
from db.factor import Factor
# Pandas to read csv file and other things
import pandas as pd
# To talk to the DB
import sqlalchemy as db
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
        urllib.request.urlretrieve(f'${URL}{filename}', f'downloads/${filename}')

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

        return ff_factors

    @staticmethod
    def fetch(engine, session, filename):
        """
        @param [sqlalchemy engine]
        @param [sqlalchemy ORM session]
        @param [string] Filename of the CSV, e.g. Emerging_5_Factors.csv
        @raise [???] If file can't be found
        @raise [???] If the file isn't a CSV
        @return [pandas.core.frame.DataFrame]
        """
        source_filename = session.query(SourceFilename).filter(SourceFilename.filename == filename).one_or_none()
        if source_filename is None:
            print(f'Factor data for ${filename} not found in the DB, backfilling it from the CSV')
            ff_data = FactorData.parse_csv(filename)
            session.add(SourceFilename(filename=filename))
            session.commit()
            source_filename = session.query(SourceFilename).filter(SourceFilename.filename == filename).one()
            ff_data['source_filename_id'] = source_filename.id
            ff_data.to_sql('factors', engine, if_exists='append', index=False)
            return ff_data
        else:
            query = session.query(Factor).filter(Factor.source_filename_id == source_filename.id)
            return pd.read_sql(query.statement, query.session.bind)
