#!/bin/bash

. ../../initialize_environment_vars.sh

cd $WORKING_DIR/etl/data

echo "Concatenating event files together"

rm -f events.txt
cat events_header.txt > events.txt
cat events.full.*.txt >> events.txt


