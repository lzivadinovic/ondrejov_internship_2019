#!/bin/bash

echo; echo Fetching enhance as submodule!;echo

REPO_ROOT=$(git rev-parse --show-toplevel)
CURR_DIR=$(pwd)

cd $REPO_ROOT

git submodule init
git submodule update

cp dataset_prep.py ./enhance

cd $CURR_DIR

