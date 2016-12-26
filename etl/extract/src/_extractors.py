from bs4 import BeautifulSoup
from requests import get

from lib.utils.util import get_path
from lib.utils.lw import get_logger, get_root_logger
from zipfile import ZipFile
from io import BytesIO
from pandas import DataFrame
from pandas.io.json import json_normalize

import tweepy, json, re, os


class EventExtractor(object):

    def __init__(self, url='http://phoenixdata.org/data', base='https://s3.amazonaws.com/oeda/data/current/'):
        """
        Download all Event files from Project Phoenix

        :param url: Link to Phoenix data
        :param base: Pattern to search for links
        """

        self.url = url
        self.base = base
        self.file_links = []

        self.data_path = get_path(__file__) + '/../../data/{0}'
        self.logger = get_logger(__name__)

    def _get_files(self):
        """
        Get links to files on S3 from Phoenix home page

        :returns list of hyperlinks to data file locations on S3
        """

        file_links = []

        page = get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        links = soup.find_all(href=re.compile(self.base))
        for link in links:
            file_links.append(link.contents[0])

        return file_links

    def extract(self):
        """
        Downloads files

        """

        files = self._get_files()

        for link in files:
            file_name = link.replace(self.base, '').replace('.zip', '')
            file_path = self.data_path.format(file_name)

            # skip file if it's been downloaded already
            if os.path.exists(file_path):
                continue

            self.logger.info('Downloading {0}'.format(file_name))
            r = get(link)

            # unzip file to data directory
            z = ZipFile(BytesIO(r.content))
            z.extractall(self.data_path.format('.'))


class TweetExtractor(object):

    def __init__(self, user):

        # initialize variables
        self.user = user

        self.loc = get_path(__file__) + '/../../{0}'
        self.logger = get_logger(__name__)

        self.logger.info('Extracting tweets for {0}'.format(user))

        # authenticate to the API
        self._initialize_api()

    def _initialize_api(self):
        """
        Handles authentication with Twitter API using tweepy.
        Requires a file at config/twitter_creds.json with the following attributes:

            "access_token":
            "access_secret":
            "consumer_token":
            "consumer_secret":

        See Twitter OAUTH docs + Tweepy docs for more details http://docs.tweepy.org/en/v3.5.0/auth_tutorial.html
        :return:
        """

        with open(self.loc.format('../config/twitter_creds.json')) as fp:
            config = json.load(fp)

        auth = tweepy.OAuthHandler(config['consumer_token'], config['consumer_secret'])
        auth.set_access_token(config['access_token'], config['access_secret'])
        self.logger.info('Successfully Authenticated to Twitter API')

        self.api = tweepy.API(auth)

    def _export_to_csv(self, df):

        file_base = self.loc.format('data/tweets_{0}.csv'.format(self.user))

        self.logger.info('Writing tweets to {0}'.format(file_base))
        df.to_csv(file_base, index=False)

    def extract(self, batch_size=200, num_tweets=2000):

        res = []

        self.logger.info('Collecting the last {0} tweets'.format(num_tweets))
        cursor = 0
        page = 1

        while cursor <= num_tweets:
            res += self.api.user_timeline(self.user, count=batch_size, page=page)
            page += 1
            cursor += batch_size

        # pick off the schema from the first tweet
        df = json_normalize(res[0]._json)
        df.drop(0, inplace=True)

        for tweet in res:
            df = df.append(json_normalize(tweet._json))

        # clean up column names a bit
        df.rename(columns=lambda x: x.replace('retweeted_status', 'rs').\
                  replace('quoted_status', 'qs').\
                  replace('.', '_'),
                  inplace=True
        )

        # write tweets to disk
        self._export_to_csv(df)

if __name__ == '__main__':

    lg = get_root_logger()

    #ex = EventExtractor()
    #ex.extract()
    twex = TweetExtractor()
    twex.extract()
    print('test')
