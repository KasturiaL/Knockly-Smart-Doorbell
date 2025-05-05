#!/bin/bash

# Gets directory path
DIR="$(dirname "$(realpath "$0")")"

# Goes to directory
cd "$DIR"

# Runs the open.py script in directory
python open.py