#!/bin/bash
set -e

. $WORKING_DIR/initialize_environment_vars.sh
cd $WORKING_DIR/etl/extract


python extract_tweets.py --user realdonaldtrump
python extract_tweets.py --user AP

