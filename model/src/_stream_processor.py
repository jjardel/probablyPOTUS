from sklearn.externals import joblib
from pandas.io.json import json_normalize
import tweepy
import json
import re
import numpy as np

from lib.utils.lw import get_logger
from lib.utils.util import get_path

# utility functions for transformations on streamed tweets


def count_uppercase_substrings(s):

    magic_regex = r"(\s+[A-Z][\w-]*)+"
    res = re.finditer(magic_regex, s)
    matches = [r for r in res]

    if matches:
        return len(matches)
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

        if status.user.id_str == '25073877':  # trump's id
            processor = TweetProcessor(status._json)
            processor.transform()
            prob_potus = processor.predict()

            if prob_potus >= 0.8:
                processor.retweet()
        else:


    def on_error(self, status_code):
        if status_code == 420:
            print('whoops, we got rate limited')  # Todo: get this into the logger
            return False


class TweetProcessor(object):

    def __init__(self, tweet):

        self.logger = get_logger(__name__)
        self.loc = get_path(__file__) + '/{0}'
        self.model = self._load_model()
        self.api = tweepy.API(AuthHandler().auth)
        self.tweet = tweet
        self.tweet_df = None

    def _load_model(self):

        self.logger.info('Loading serialized model')

        # hardcoded path
        path = self.loc.format('../saved_models/model.pkl')

        return joblib.load(path)

    def transform(self):

        tweet_df = json_normalize(self.tweet)

        # drop all columns from tweet_df that we're not using in extract_fields
        with open(self.loc.format('../../etl/extract/extract_fields.json')) as fp:
            fields_dict = json.load(fp)
            fields_subset = fields_dict.get('fields')

        tweet_df = tweet_df.loc[:, fields_subset]

        # perform transformations on DF to get into same form as DB table
        tweet_df.loc[:, 'retweets_to_faves'] = 0

        # this feature isn't scaled properly since we're pulling from the stream
        #tweet_df.loc[:, 'retweets_to_faves'] = tweet_df.loc[:, 'retweet_count'] / tweet_df.loc[:, 'favorite_count']
        tweet_df.loc[:, 'num_characters'] = tweet_df.text.apply(lambda x: len(x))
        tweet_df.loc[:, 'num_exclamation_points'] = tweet_df.text.apply(lambda x: x.count('!'))
        tweet_df.loc[:, 'is_tweetstorm'] = 0
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

    def predict(self):

        return self.model.gs_.predict_proba(self.tweet_df)[0][1]

    def retweet(self):

        # retweet with boilerplate
        prob = self.predict()

        text = 'There is a {:.0%} chance that this tweet was written by POTUS https://twitter.com/realDonaldTrump/status/{}'.\
            format(prob, self.tweet_df.id_str.loc[0])

        self.api.update_status(text)
        self.logger.info('Retweeted tweet ID {0}'.format(self.tweet_df.id_str.loc[0]))


if __name__ == '__main__':

    auth = AuthHandler()

    api = tweepy.API(auth_handler=auth.auth)
    tweet = api.get_status('741286391200505857')

    p = TweetProcessor(
        tweet=tweet._json
    )
    p.transform()
    p.retweet()

    print('test')




