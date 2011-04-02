#!/usr/bin/env bash

find . -iname '*.pyc' -print0 | xargs -0 rm
rm c10t.log
