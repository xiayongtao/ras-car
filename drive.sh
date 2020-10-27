#!/bin/bash
echo "Hello World !"

cd "$(dirname $0)"
nohup python index.py &
