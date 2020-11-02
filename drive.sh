#!/bin/bash
echo "Hello World !"

sudo sudo kill -9 $(lsof -i:8080 -t)

cd "$(dirname $0)"
nohup python index.py &
