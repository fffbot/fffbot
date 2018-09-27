#!/bin/sh

GIT_HASH=`git rev-parse --verify HEAD`
BUILD_DATE=`date --iso-8601=seconds`

docker build \
    --build-arg git_hash=${GIT_HASH} \
    --build-arg build_date=${BUILD_DATE} \
    --no-cache \
    . -t fffbot
