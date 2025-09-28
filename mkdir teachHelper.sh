#!/bin/sh

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
python3 -m venv .venv
sudo apt update
sudo apt install cloud-init
source .venv/bin/activate
pip install -r requirements.txt