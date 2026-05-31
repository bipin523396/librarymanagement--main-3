#!/usr/bin/env bash

# initialize_git.sh - Set up Git remote and push initial commit

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Initialize git repository if it doesn't exist
if [ ! -d ".git" ]; then
  echo "Initializing new git repository..."
  git init
else
  echo "Git repository already initialized."
fi

# Add all files
git add .

# Commit (allow empty if already committed)
if git diff-index --quiet HEAD --; then
  echo "No changes to commit."
else
  git commit -m "Initial commit"
fi

# Set remote origin (replace with your GitHub repo URL)
REMOTE_URL="https://github.com/bipin523396/librarymanagement--main-3.git"
if git remote get-url origin 2>/dev/null; then
  echo "Remote 'origin' already set. Updating URL if needed..."
  git remote set-url origin "$REMOTE_URL"
else
  echo "Adding remote 'origin'..."
  git remote add origin "$REMOTE_URL"
fi

# Push to GitHub (create master/main branch if needed)
# Detect default branch name
DEFAULT_BRANCH=$(git symbolic-ref --short HEAD || echo "main")

echo "Pushing to remote 'origin'..."
git push -u origin "$DEFAULT_BRANCH"

echo "Git setup complete."
