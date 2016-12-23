from lib.utils.db_conn import DBConn
from lib.utils.lw import get_logger

from pandas import read_csv


class FileLoader(object):

    def __init__(self, creds_file, data_file, table, schema, delim=','):

        self.logger = get_logger(__name__)

        self.file = data_file
        self.table = table
        self.schema = schema
        self.delim = delim
        self.conn = None

        self._create_connection(creds_file)

    def _create_connection(self, creds_file):

        self.conn = DBConn(creds_file)

    def load(self):

        self.logger.info(self.delim)
        df = read_csv(self.file, error_bad_lines=False, sep=self.delim)
        self.conn.load(df, self.table, self.schema, if_exists='replace')


if __name__ == '__main__':

    loader = FileLoader(creds_file='/Users/jjardel/dev/distractingdonald/config/db_creds.json',
                       data_file='/Users/jjardel/dev/distractingdonald/etl/data/tweets.csv',
                       table='tweets',
                       schema='raw'
    )

    loader.load()
