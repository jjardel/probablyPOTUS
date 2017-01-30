#!/usr/bin/env bash

set -e

. $WORKING_DIR/initialize_environment_vars.sh

extract/extract.sh
load/load.sh
transform/transform.sh
