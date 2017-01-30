# python STL
import re
import os
import numpy as np
from datetime import datetime

# sklearn modules
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

# model utils
from model.src import DFColumnExtractor, twitter_tokenizer

# other utils
from lib.utils.lw import get_logger
from lib.utils.db_conn import DBConn

WORKING_DIR = os.getenv('WORKING_DIR')

CONFIG = '{0}/config/db_creds_local.json'.format(WORKING_DIR)

TEXT_FEATURES = 'text'

NON_TEXT_FEATURES = [
    'favorites',
    'retweets',
    'retweets_to_faves',
    'num_exclamation_points',
    'num_uppercase_strings',
    'is_trump_retweet'
    #'is_tweetstorm'   # this feature has some leakage of the label
]

LABEL = 'tweet_source'


class BaseModel(object):

    def __init__(self, table_name, schema_name, **params_dict):

        self.table_name = table_name
        self.schema_name = schema_name
        self.logger = get_logger(__name__)
        self.params = params_dict
        self._random_state = 42

        self.data = None
        self.train_inds_ = None
        self.test_inds_ = None
        self.model_ = None
        self.gs_ = None

    @property
    def _estimator(self):

        raise NotImplementedError('this method must be overriden')

    def _get_data(self):

        # retreive data from DB
        conn = DBConn(CONFIG)
        data = conn.export(self.table_name, schema=self.schema_name)

        # zero-one encoding for labels
        data.tweet_source = data.tweet_source.apply(lambda x: 1 if x == 'android' else 0)

        # standardize all urls
        data.text = data.text.str.replace('https?:\/\/t.co\/[a-zA-Z0-9\-\.]{8,}', 'twitter_url ')

        self.data = data

    def _get_train_test_split(self, train_size=None):
        """
        Perform stratified train/test split.  Sets the indices for the train/test sets
        """

        idx_array = np.arange(len(self.data))

        self.train_inds_, self.test_inds_, _, _ = train_test_split(
            idx_array,
            self.data[LABEL].values,
            train_size=train_size,
            stratify=self.data[LABEL].values,
            random_state=self._random_state
        )

    def train(self, train_size=0.8, k_folds=5):

        # retrieve data from DB and pre-process
        self._get_data()

        # perform train/test split
        self._get_train_test_split(train_size=train_size)

        # define text pre-processing pipeline
        text_pipeline = Pipeline([
            ('extract_text', DFColumnExtractor(TEXT_FEATURES)),
            ('vect', TfidfVectorizer(tokenizer=twitter_tokenizer))
        ])

        # define pipeline for pre-processing of numeric features
        numeric_pipeline = Pipeline([
            ('extract_nums', DFColumnExtractor(NON_TEXT_FEATURES)),
            ('scaler', MinMaxScaler())
        ])

        # combine both steps into a single pipeline
        pipeline = Pipeline([
            ('features', FeatureUnion([
                ('text_processing', text_pipeline),
                ('num_processing', numeric_pipeline)
            ])),
            ('clf', self._estimator)
        ])

        self.logger.info('Fitting model hyperparameters with {0}-fold CV'.format(k_folds))
        gs = GridSearchCV(pipeline, self.params, n_jobs=-1, cv=k_folds)

        X = self.data.iloc[self.train_inds_, :]
        y = self.data[LABEL].values[self.train_inds_]

        gs.fit(X, y)

        self.logger.info('Validation set accuracy is {0}'.format(gs.best_score_))

        self.gs_ = gs
        self.model_ = gs.best_estimator_

    def evaluate(self):

        if not self.model_:
            raise AttributeError('No model attribute found.  Must run train() method first')

        X_test = self.data.iloc[self.test_inds_, :]
        y_test = self.data[LABEL].values[self.test_inds_]

        y_preds = self.model_.predict(X_test)

        self.logger.info('test set accuracy is {0}'.format(accuracy_score(y_test, y_preds)))

    def save(self, filebase):

        # re-train best model on full data set
        self.model_.fit(self.data, self.data[LABEL].values)

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')

        # logging wrappers don't serialize
        del self.logger

        joblib.dump(self,'{0}/model_{1}.pkl'.format(filebase, ts))


class NaiveBayesModel(BaseModel):

    @property
    def _estimator(self):

        return MultinomialNB()


class RandomForestModel(BaseModel):

    @property
    def _estimator(self):

        return RandomForestClassifier()


if __name__ == '__main__':

    nb_params = {
        'features__text_processing__vect__ngram_range': [(1, 1), (1, 2), (1, 3)],
        'clf__alpha': np.logspace(-2, 0, num=10)
    }

    m = NaiveBayesModel('crazy_tweet_features', 'clean', **nb_params)
    m.train()
    m.save('.')

    print('test')