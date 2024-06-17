#! /bin/bash

git submodule foreach --recursive 'branch=$(git branch -r --contains | grep -v "\->" | head -n 1 | sed "s/ *origin\///"); git checkout -B $branch origin/$branch || echo "No remote branch found for submodule: $(pwd)"'