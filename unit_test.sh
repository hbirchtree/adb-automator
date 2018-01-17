#!/bin/bash

function adb_run()
{
    $(dirname $0)/adb-auto.py $@
}

function adb_exe()
{
    adb $@
}

set -e

adb_run install $1

# No touch. Lots of effort to make this POS work.
DEVICE_DATE=`date +"%m-%d %H:%M:%S.000"`

# Account for difference in time, just in case
sleep 1

adb_run start $2

# Let the app run for a bit...
sleep 2

# Wait for result
echo "Log entries since '$DEVICE_DATE'"
adb logcat -T "$DEVICE_DATE" -e "CoffeeTest::result.*" | while read LOGLINE
do
    [[ "${LOGLINE}" == *"CoffeeTest"* ]] && pkill -P $$ adb
done

echo "Test finished"

# Stop the app
adb_run stop $2

# Uninstall the app, too
adb_run uninstall $2
