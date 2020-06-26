#!/bin/bash

# 2020/06 BuRnCycL 
# Init Virtual Environment

rm -rf ./venv
virtualenv -p python3 ./venv
source ./venv/bin/activate
pip3 install -r ./requirements.txt

# Use `deactivate` to exit Python3 virtual environment.

