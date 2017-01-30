#!/bin/bash
set -e

. $WORKING_DIR/initialize_environment_vars.sh
cd $WORKING_DIR/etl/transform

$WORKING_DIR/lib/utils/bin/psqlwrapper.sh $WORKING_DIR/etl/transform/001_clean_tweets.sql
$WORKING_DIR/lib/utils/bin/psqlwrapper.sh $WORKING_DIR/etl/transform/002_create_features.sql

