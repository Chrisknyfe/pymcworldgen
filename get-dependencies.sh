#!/usr/bin/env bash

# gets the dependencies for pyMCWorldGen automatically.
# Works best on a linux build that uses apt-get

# pymclevel
wget --no-check-certificate https://github.com/codewarrior0/pymclevel/zipball/master
unzip master
mv codewarrior0-pymclevel-* pymclevel
rm master

# c10t
wget --no-check-certificate http://toolchain.eu/minecraft/c10t/releases/c10t-1.6-linux-x86.tar.gz
gzip -dc c10t-1.6-linux-x86.tar.gz | tar xf -
rm c10t-1.6-linux-x86.tar.gz
mv c10t* c10t

# Python dependencies
sudo apt-get install python python-numpy python-scipy python-matplotlib

