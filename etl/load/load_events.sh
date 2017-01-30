#!/bin/bash
set -e

. $WORKING_DIR/initialize_environment_vars.sh

./prep_events.sh
$WORKING_DIR/lib/utils/bin/psqlwrapper.sh create_events_table.sql

cd $WORKING_DIR/etl/data
pg_bulkload -d postgres -i events.txt -O raw.events -o $'DELIMITER=\t' -o $'PARSE_ERRORS=-1' || :

