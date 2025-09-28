#!/bin/sh

apt update
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python3.12 python3.12-venv python3.12-dev -y


mkdir teachHelper
cd teachHelper/
git init
git remote add origin https://github.com/AlixanGalachiev/TeachHelper.git
git pull origin main
git switch main
git branch -D master
tourch .env
mkdir pulic
mv pulic/ public
cd public/
mkdir work task
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
sudo apt install -y python3.12-dev libpq-dev build-essential
pip install -r requirements.txt
