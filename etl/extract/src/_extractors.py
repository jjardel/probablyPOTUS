from lib.utils.util import get_path
from lib.utils.lw import get_logger, get_root_logger
from pandas import DataFrame
from pandas.io.json import json_normalize

import tweepy, json


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

    def _get_extraction_fields(self):

        try:
            with open(self.loc.format('extract/extract_fields.json')) as fp:
                fields_dict = json.load(fp)
        except FileNotFoundError:
            raise FileNotFoundError('User must supply an extract_fields.json file to identify which fields to extract from Tweets')

        return fields_dict.get('fields')

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

        fields = self._get_extraction_fields()
        df = DataFrame(columns=fields)

        for tweet in res:
            tmp_df = json_normalize(tweet._json)
            df = df.append(tmp_df.ix[:, fields])

        # clean up column names a bit
        df.rename(columns=lambda x: x.replace('.', '_'), inplace=True)

        # write tweets to disk

        self._export_to_csv(df)

if __name__ == '__main__':

    lg = get_root_logger()

    twex = TweetExtractor()
    twex.extract()
    print('test')
