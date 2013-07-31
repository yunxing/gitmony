#!/bin/sh
cd $1
git reset --hard
git pull
cd -
