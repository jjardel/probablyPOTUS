from sklearn.base import BaseEstimator, TransformerMixin
from nltk.tokenize import TweetTokenizer


class DFColumnExtractor(BaseEstimator, TransformerMixin):
    def __init__(self, column_set=None):

        self.column_set = column_set
        if not self.column_set:
            raise BaseException('must set a list of columns to be extracted from the DF')

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.column_set].values


def twitter_tokenizer(x):

    return TweetTokenizer(strip_handles=True).tokenize(x)

