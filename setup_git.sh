#!/bin/sh
if [ -d "git_reader" ]; then
    exit 0
fi
git clone git@github.com:yunxing/finance-725.git git_reader
