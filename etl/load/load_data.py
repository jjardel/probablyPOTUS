from etl.load.src import FileLoader
from lib.utils.lw import get_header, get_root_logger

import argparse


def main(args):

    loader = FileLoader(args.config, args.file, args.table, args.schema, delim=args.delim)
    loader.load()

if __name__ == '__main__':

    logger = get_root_logger()
    _ = get_header(logger, 'Loading CSV data')

    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    parser.add_argument('--file')
    parser.add_argument('--table')
    parser.add_argument('--schema')
    parser.add_argument('--delim', default=',')

    args = parser.parse_args()

    if args.delim == 'tab':
        args.delim = '\t'

    main(args)
