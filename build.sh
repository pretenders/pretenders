#!/bin/bash
set -e
nosetests pretenders/http/tests
pep8 pretenders
(cd docs; make clean html)
