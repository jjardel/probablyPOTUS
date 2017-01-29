from model.src import RandomForestModel, NaiveBayesModel

from lib.utils.lw import get_root_logger, get_header
from lib.utils.util import get_path


def main(table, schema):

    logger = get_root_logger()
    _ = get_header(logger, 'Building a model to predict Trump tweets')

    loc = get_path(__file__) + '/{0}'

    model = RandomForestModel(table, schema)
    model.train()
    model.evaluate()
    model.save(loc.format('saved_models'))


if __name__ == '__main__':

    main('crazy_tweet_features', 'clean')