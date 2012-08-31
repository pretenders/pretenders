#!/bin/bash
#set -e

# start boss process in background
echo "[Pretenders] Starting Boss server"
python -m pretenders.boss.server --host localhost --port 8000 >boss.out 2>boss.err &
sleep 2

# run tests
echo "[Pretenders] Running tests"
nosetests -s pretenders/http/tests pretenders/smtp/tests

# sleep to allow for stale servers to be deleted
echo "[Pretenders] Letting maintainer kill stale servers"
sleep 20

# terminate boss
echo "[Pretenders] Terminating boss processes"
kill -11 `cat maintain-boss.pid`
sleep 2
kill -11 `cat pretenders-boss.pid`

# PEP8 and documentation...
pep8 pretenders > pep8.txt || echo "PEP8 errors"
(cd docs; make clean html)
