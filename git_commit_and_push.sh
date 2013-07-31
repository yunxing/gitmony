#!/bin/sh
cd $1
git commit --allow-empty -F $2
git push
cd -
