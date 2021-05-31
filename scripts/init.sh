#!/usr/bin/env bash

marshall_clone_uri=$(grep MARSHALL_CLONE_URI .env | cut -d '=' -f2 | sed "s/\"//g")
git clone $marshall_clone_uri

marshall_py_version=$(cat marshall/.python-version)

pyenv install $marshall_py_version
pyenv local $marshall_py_version

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

cd marshall/backend
cp .env-example .env

sed -i -e 's/^TWILIO_ACCOUNT_SID.*$/TWILIO_ACCOUNT_SID="invalid_account_sid"/g' .env
sed -i -e 's/^TWILIO_AUTH_TOKEN.*$/TWILIO_AUTH_TOKEN="invalid_auth_token"/g' .env


poetry install
