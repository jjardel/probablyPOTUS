from etl.extract.src import TweetExtractor
from lib.utils.lw import get_root_logger, get_header

import argparse


def main(user):

    twex = TweetExtractor(user)
    twex.extract()


if __name__ == '__main__':

    logger = get_root_logger()
    _ = get_header(logger, 'Tweet Extractor')

    parser = argparse.ArgumentParser()
    parser.add_argument('--user', help='enter the twitter handle of the user to extract tweets')

    args = parser.parse_args()

    main(args.user)

