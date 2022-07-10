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
pytest -vv
test_result=$?
if test ! $test_result -eq 0
then
    echo "Tests failed. Boss output"
    cat boss.out 
    cat boss.err
    echo "End of Boss Output"
fi

# sleep to allow for stale servers to be deleted
echo "[Pretenders] Letting maintainer kill stale servers"
sleep 6

# terminate boss
echo "[Pretenders] Terminating boss processes"
kill -9 `cat maintain-boss.pid`
kill -11 `cat pretenders-boss.pid`

# PEP8 and documentation...
pycodestyle --exclude=common pretenders > pep8.txt || echo "PEP8 errors"
(cd docs; make clean html)

exit $test_result