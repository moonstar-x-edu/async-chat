#!/bin/bash

python3 server/main.py &
python3 client/main.py localhost 10023 u1 &
python3 client/main.py localhost 10023 u2
