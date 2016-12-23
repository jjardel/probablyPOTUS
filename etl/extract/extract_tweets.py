from etl.extract.src import TweetExtractor
from lib.utils.lw import get_root_logger, get_header


def main():

    twex = TweetExtractor()
    twex.extract()


if __name__ == '__main__':

    logger = get_root_logger()
    _ = get_header(logger, 'Extracting Trump Tweets...hold your nose')

    main()

