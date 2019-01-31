#!/bin/bash

GIT_HASH=`git rev-parse --verify HEAD`
BUILD_DATE=`date --iso-8601=seconds`


SHORT_HASH=$(git rev-parse --short HEAD)
IS_DIRTY=$(git diff --quiet && echo 0 || echo 1)


SUFFIX=

if [[ ${IS_DIRTY} -eq 1 ]]; then
  echo Dirty workdir, using _d suffix. Git status:
  git status -s
  SUFFIX=_d
else
  echo Workdir is clean
fi

TAG_NAME=${SHORT_HASH}${SUFFIX}


docker build \
    --build-arg git_hash=${GIT_HASH} \
    --build-arg build_date=${BUILD_DATE} \
    --no-cache \
    -t fffbot:${TAG_NAME} .
