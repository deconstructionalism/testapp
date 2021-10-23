#!/usr/bin/env bash

# helper function to pretty print titles for logical sections
title_print () {
  echo ""
  echo $1
  echo "--------------------"
}

# var to hold output in case of update
output=

if [[ $1 == "init" ]]; then
  # if "init" args is passed, clone the marshall repository locally
  title_print "CLONING MARSHALL REPO"
  marshall_clone_uri="$(grep MARSHALL_REPO_BASE_URL .env | cut -d '=' -f2 | sed "s/\"//g").git"
  git clone $marshall_clone_uri
else
  # pull the most recent commits from the appropriate branch
  title_print "UPDATING MARSHALL REPO"
  marshall_branch=$(grep MARSHALL_BRANCH .env | cut -d '=' -f2 | sed "s/\"//g")
  output=$(git -C marshall/ pull --force origin $marshall_branch)
fi

# if the branch is already up to date, exit the script with an error return code
if [[ $output == *"Already up to date."* ]]; then
  echo "MARSHALL repo already up to date"
  exit 1
fi

# determine which python version is being used by marshall and
# install it to pyenv
title_print "INSTALLING MARSHALL PYTHON VERSION IF NOT INSTALLED"
marshall_py_version=$(cat marshall/.python-version)
pyenv install --skip-existing $marshall_py_version
pyenv local $marshall_py_version

# set the virtual env folder to `.venv` if it doesn't exist, activate
# the virtual env
title_print "ACTIVATING VIRTUAL ENV"
python -m venv .venv
source .venv/bin/activate

# copy over most up-to-date .env file for marshall from `.env-example` and
# add dummy variables for env vars that otherwise will throw errors
title_print "CONFIGURING MARSHALL ENV"
cd marshall/backend
cp .env-example .env
sed -i -e 's/^TWILIO_ACCOUNT_SID.*$/TWILIO_ACCOUNT_SID="invalid_account_sid"/g' .env
sed -i -e 's/^TWILIO_AUTH_TOKEN.*$/TWILIO_AUTH_TOKEN="invalid_auth_token"/g' .env

# update python in virtual env
title_print "UPDATING PIP"
python -m pip install --upgrade pip

# install packages for marshall
title_print "INSTALLING MARSHALL POETRY PACKAGES"
poetry install

# install summarizer poetry packages
cd ../..
title_print "INSTALLING SUMMARIZER POETRY PACKAGES"
poetry install
