#!/bin/bash

git pull
nohup bin/build.sh FASTALL &> fastall.log &

