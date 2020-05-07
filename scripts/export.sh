#!/bin/bash
echo "Running Script..."
cd ~/covid-19
git pull

cd ~/covid-19-tools/code
git pull

python3 export.py

git add ../data/data_standard.txt
git add ../data/world.p

d=`date +%m-%d-%Y`
git commit -m "Daily Update - ${d}"

git push

cd ~/covid-19-tools/scripts
echo "Done."
