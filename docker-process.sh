#!/bin/sh

set -ex

mkdir -p /models/tilted/

python /models/tilt_process.py
python /models/next_gen.py
python /models/next_gen_extrude.py

