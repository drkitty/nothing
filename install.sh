#!/usr/bin/env bash

for f in requirements/*; do
    pip3 install -r "$f"
done
