#!/usr/bin/env bash

set -e

export WORKING_DIR=/Users/jjardel/dev/distractingdonald # Todo: initialize someplace else

. $WORKING_DIR/initialize_environment_vars.sh

extract/extract.sh
load/load.sh
