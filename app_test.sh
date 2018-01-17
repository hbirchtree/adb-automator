#!/bin/bash

SCRIPT_WD=$(dirname $0)

function adb_run() {
	"$SCRIPT_WD/adb-auto.py" $@
}

adb_run info

adb_run install "$1"
adb_run start "$2"
sleep 2
adb_run screenshot "%DEVICE_UUID%.png"
adb_run simulate tap 50 50
sleep 1
adb_run stop "$2"

