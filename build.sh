#!/bin/bash
set -e
nosetests pretenders/http/tests pretenders/smtp/tests
pep8 pretenders > pep8.txt || echo "PEP8 errors"
(cd docs; make clean html)
