from sklearn.externals import joblib
from pandas.io.json import json_normalize
import tweepy
import json
import re
import numpy as np

from lib.utils.lw import get_logger
from lib.utils.util import get_path


def count_uppercase_substrings(s):
    res = re.match('([A-Z][\w-]*(\s+[A-Z][\w-]*)+)', s)
    if res:
        return len(res)
    else:
        return 0

def normalize_tweet_sources(x):

    if 'android' in x.lower():
        return 'android'
    elif 'iphone' in x.lower() or 'ipad' in x.lower():
        return 'iphone'
    elif 'twitter web client' in x.lower():
        return 'web'
    elif 'socialflow' in x.lower():
        return 'socialflow'
    else:
        return 'other'

def is_retweet(x):

    if x.startswith('"@') or x.startswith('RT'):
        return 1
    else:
        return 0


class AuthHandler(object):

    def __init__(self):
        self.logger = get_logger(__name__)
        self.loc = get_path(__file__) + '/{0}'

        config = self._load_credentials()
        self.auth = self._handle_auth(config)

    def _load_credentials(self):

        with open(self.loc.format('../../config/twitter_creds.json')) as fp:

            config = json.load(fp)

        self.logger.info('Twitter credentials loaded')

        return config

    def _handle_auth(self, config):

        auth = tweepy.OAuthHandler(config['consumer_token'], config['consumer_secret'])
        auth.set_access_token(config['access_token'], config['access_secret'])

        return auth


class Listener(tweepy.StreamListener):

    def on_status(self, status):

        processor = TweetProcessor(status._json)
        processor.transform()


class TweetProcessor(object):

    def __init__(self, model_pkl, auth, tweet):

        self.logger = get_logger(__name__)
        self.loc = get_path(__file__) + '/{0}'
        self.model = self._load_model(model_pkl)
        self.api = tweepy.API(auth)
        self.tweet = tweet
        self.tweet_df = None

    def _load_model(self, filepath):

        self.logger.info('Loading serialized model from {0}'.format(filepath))

        return joblib.load(filepath)

    def transform(self):

        tweet_df = json_normalize(self.tweet)

        # drop all columns from tweet_df that we're not using in extract_fields
        with open(self.loc.format('../../etl/extract/extract_fields.json')) as fp:
            fields_dict = json.load(fp)
            fields_subset = fields_dict.get('fields')

        tweet_df = tweet_df.loc[:, fields_subset]

        # perform transformations on DF to get into same form as DB table
        tweet_df.loc[:, 'retweets_to_faves'] = tweet_df.loc[:, 'retweet_count'] / tweet_df.loc[:, 'favorite_count']
        tweet_df.loc[:, 'num_characters'] = tweet_df.text.apply(lambda x: len(x))
        tweet_df.loc[:, 'num_exclamation_points'] = tweet_df.text.apply(lambda x: x.count('!'))
        tweet_df.loc[:, 'is_tweetstorm'] = np.nan
        tweet_df.loc[:, 'is_trump_retweet'] = tweet_df.text.apply(lambda x: is_retweet(x))
        tweet_df.loc[:, 'num_uppercase_strings'] = tweet_df.text.apply(lambda x: count_uppercase_substrings(x))
        tweet_df.loc[:, 'source'] = tweet_df.source.apply(lambda x: normalize_tweet_sources(x))

        tweet_df.rename(columns={
            'favorite_count': 'favorites',
            'quoted_status.text': 'quoted_status_text',
            'retweet_count': 'retweets',
            'source': 'tweet_source',
            'user.id_str': 'user_id_str',
            'user.name': 'user_name',
            'user.followers_count': 'followers',
            'user.screen_name': 'user_screen_name',
            'user.statuses_count': 'num_statuses'

        }, inplace=True)

        self.tweet_df = tweet_df


        print("test")

    def retweet(self):

        # call model.predict(), if prob > threshold
        pass


if __name__ == '__main__':

    auth = AuthHandler()

    api = tweepy.API(auth_handler=auth.auth)
    tweet = api.get_status('741286391200505857')

    p = TweetProcessor(
        model_pkl='/Users/jjardel/dev/probablyPOTUS/model/saved_models/model_20170129_140655.pkl',
        auth=auth,
        tweet=tweet._json
    )
    p.transform()

    print('test')




