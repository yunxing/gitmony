#!/bin/sh
cd $1
git commit -a -C HEAD --amend
git push -f
cd -
