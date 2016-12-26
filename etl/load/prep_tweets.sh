#!/bin/bash

. ../../initialize_environment_vars.sh

cd $WORKING_DIR/etl/data

echo "Concatenating tweet files together\n\n"

rm -f tweets.csv tmp
for f in `ls tweets_*.csv`; do
    echo "processing $f"
    cat $f | sed -n '1!p' >> tmp
done

head -1 $f > tweets.csv
cat tmp >> tweets.csv

rm -f tmp


