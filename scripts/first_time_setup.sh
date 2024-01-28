#! /bin/bash
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #gets the current directory

#move to the project root folder
cd "$SCRIPT_DIR"/..
git submodule update --init --recursive
CONTAINER_NAME=${PWD##*/}  

git config --global pull.rebase false
git remote add template https://github.com/blooop/repo_b.git
git fetch --all
git checkout main && git pull origin main
git merge template/main  --allow-unrelated-histories -m 'feat: pull changes from remote template'

$SCRIPT_DIR/rename_project.sh $CONTAINER_NAME
git commit -a -m 'rename project to $CONTAINER_NAME'

git merge template/main --strategy-option ours --allow-unrelated-histories -m 'feat: pull changes from remote template'
git remote remove template

git push