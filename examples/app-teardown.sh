#!/bin/sh

DIR=`dirname "$0"`

cd $DIR
export FLASK_APP=app.py

# clean environment
find . -name "*.mo" -exec rm '{}' \;
