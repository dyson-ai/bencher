#!/bin/bash

# Update submodules recursively, commit, and push changes within each submodule
git submodule foreach --recursive '
  branch=$(git branch -r --contains HEAD | grep -v "\->" | head -n 1 | sed "s/ *origin\///")
  if [ -z "$branch" ]; then
    echo "No branch found for submodule: $(pwd)"
    exit 0
  fi
  echo "Checking out branch $branch for submodule $(pwd)"
  git checkout -B $branch origin/$branch || {
    echo "Failed to checkout branch $branch for submodule: $(pwd)"
    exit 1
  }
  echo "Pulling latest changes for submodule $(pwd)"
  git pull origin $branch || {
    echo "Failed to pull latest changes for submodule: $(pwd)"
    exit 1
  }
  if ! git diff-index --quiet HEAD --; then
    echo "Committing changes in submodule $(pwd)"
    git commit -am "Update submodule to latest commit on branch $branch" || {
      echo "Failed to commit changes in submodule: $(pwd)"
      exit 1
    }
    echo "Pushing changes for submodule $(pwd) on branch $branch"
    git push origin "$branch" || {
      echo "Failed to push changes for submodule: $(pwd)"
      exit 1
    }
  fi
'

# Commit all changes in the main repository
echo "Committing all submodule updates in the main repository"
git add --all
git commit -m "Update submodules to latest commits on their respective branches"

# Push changes in the main repository
main_branch=$(git branch --show-current)
if [ -z "$main_branch" ]; then
  echo "No branch found for main repository"
  exit 0
fi
echo "Pushing changes in the main repository on branch $main_branch"
git push origin "$main_branch" || {
  echo "Failed to push changes in the main repository"
  exit 1
}
