#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"

cd "$DIR"

python knownface.py