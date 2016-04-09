#!/bin/bash
rm -f test_server.log
mongo 'bnw_test' --eval 'printjson(db.dropDatabase())'
/tmp/venv/bin/pip install coverage
/tmp/venv/bin/python run.py
ECODE="$?"
echo
if [ "$ECODE" == "0" ]; then
    /tmp/venv/bin/python -m coverage html --include='*/BnW-*'
    echo -e "\033[1;32mAll tests passed.\033[0m"
else
    echo -e "\033[1;31mSome test failed.\033[0m"
fi
echo
exit "$ECODE"

