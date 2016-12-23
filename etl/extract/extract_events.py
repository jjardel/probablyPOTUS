from etl.extract.src import EventExtractor
from lib.utils.lw import get_root_logger, get_header


def main():

    ex = EventExtractor()
    ex.extract()


if __name__ == '__main__':

    logger = get_root_logger()
    _ = get_header(logger, 'Extracting World Events from Project Phoenix')

    main()

