#!/bin/bash
#set -e

# Add this directory to the python path
export PYTHONPATH="`dirname $0`"

# start boss process in background
echo "[Pretenders] Starting Boss server"
python -m pretenders.boss.server --host localhost --port 8000 --timeout 2 >boss.out 2>boss.err &
sleep 2

# run tests
echo "[Pretenders] Running tests"
nosetests --verbosity=2 -s pretenders

# sleep to allow for stale servers to be deleted
echo "[Pretenders] Letting maintainer kill stale servers"
sleep 6

# terminate boss
echo "[Pretenders] Terminating boss processes"
kill -9 `cat maintain-boss.pid`
kill -11 `cat pretenders-boss.pid`

# PEP8 and documentation...
pep8 pretenders > pep8.txt || echo "PEP8 errors"
(cd docs; make clean html)
