#!/bin/bash
set -e

export WORKING_DIR=/Users/jjardel/dev/distractingdonald # Todo: initialize someplace else

. $WORKING_DIR/initialize_environment_vars.sh
cd $WORKING_DIR/etl/extract


python extract_tweets.py
python extract_events.py

