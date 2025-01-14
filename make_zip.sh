#!/bin/sh
sudo find . -name "__pycache__" -exec rm -rf {} \;
cp LICENSE.txt rgd/LICENSE
zip -r ../rgd_plugin.zip rgd/ --exclude=.git/*
rm rgd/LICENSE

