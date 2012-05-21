#!/bin/bash
set -e
nosetests pretenders/http/tests
pep8 pretenders > pep8.txt || echo "PEP8 errors"
(cd docs; make clean html)
