from numpy import logspace

from model.src import RandomForestModel, NaiveBayesModel

from lib.utils.lw import get_root_logger, get_header
from lib.utils.util import get_path


def main(table, schema):

    logger = get_root_logger()
    _ = get_header(logger, 'Building a model to predict Trump tweets')

    loc = get_path(__file__) + '/{0}'

    params = {
        'features__text_processing__vect__ngram_range': [(1, 1), (1, 2), (1, 3)],
        'clf__n_estimators': [int(x) for x in logspace(1, 3, num=10)]
    }

    model = RandomForestModel(table, schema, **params)
    model.train()
    model.evaluate()
    model.save(loc.format('saved_models'))


if __name__ == '__main__':

    main('crazy_tweet_features', 'clean')