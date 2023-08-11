#!/bin/bash

cd tmpgit
git init
git checkout -b $1
git remote add origin $2
git commit -m "publish $1"
git push origin $2 -f