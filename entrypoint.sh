#!/bin/bash


pg_ctlcluster 12 main start 
su - postgres -c "psql -c 'CREATE ROLE ROOT SUPERUSER LOGIN'" 2>>/dev/null

set -e
echo "GOING"
PYTHONPATH="." pytest-3 tests/