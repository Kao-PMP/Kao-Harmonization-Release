#!/usr/bin/env bash

for file in *.dump
do
    echo " ============= $file ========== "
    diff $file backups
done

