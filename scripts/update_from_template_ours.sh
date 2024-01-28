#! /bin/bash

git config --global pull.rebase false
git remote add template https://github.com/blooop/python_template.git
git fetch --all
git checkout main && git pull origin main
git checkout -B feature/update_from_template; git pull
git merge template/main --strategy-option ours --allow-unrelated-histories -m 'feat: pull changes from remote template'
git remote remove template
git push origin feature/update_from_template