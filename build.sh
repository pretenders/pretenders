#!/bin/bash
#set -e

# Add this directory to the python path
export PYTHONPATH="`dirname $0`"

# start boss process in background
echo "[Pretenders] Starting Boss server"
./runboss.sh >boss.out 2>boss.err &
sleep 2

# run tests
echo "[Pretenders] Running tests"
nosetests -vv

# sleep to allow for stale servers to be deleted
echo "[Pretenders] Letting maintainer kill stale servers"
sleep 6

# terminate boss
echo "[Pretenders] Terminating boss processes"
kill -9 `cat maintain-boss.pid`
kill -11 `cat pretenders-boss.pid`

# PEP8 and documentation...
pep8 --exclude=common pretenders > pep8.txt || echo "PEP8 errors"
(cd docs; make clean html)
