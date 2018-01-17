#!/usr/bin/python3

from subprocess import Popen, PIPE;
from os import environ
from os.path import dirname


def popen_proc(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE);
    return p.communicate(), p


def popen_shell(cmd):
    print("-" * 20, "INTERACTIVE", "-"*20)
    p = Popen(cmd)
    return (0, 0), p


def adb_exec(cmd,  live_output=False):
    #adb_path = environ["ANDROID_SDK"] + "/platform-tools/adb"
    adb_path = "adb"
    if live_output:
        return popen_shell([adb_path] + cmd)
    else:
        return popen_proc([adb_path] + cmd)


def monkeyrun(script, args):
    monkeyrunner_bin = environ["ANDROID_SDK"] + "/tools/bin/monkeyrunner"
    return popen_proc([monkeyrunner_bin, dirname(__file__) + "/" + script] + args)


def adb_dev_exec(dev, cmd, live_output=False):
    if live_output:
        (stdout, stderr), p = adb_exec(["-s", dev]+cmd, True)
    else:
        (stdout, stderr), p = adb_exec(["-s", dev]+cmd)

    p.wait()
    if live_output:
        print("-" * 20, "END INTERACTIVE", "-"*20)

    if p.returncode != 0:
        print(stdout.decode())
        raise RuntimeError(stderr.decode())

    return stdout.decode().replace('\r\n','\n')


def adb_get_prop(dev, prop):
    return adb_dev_exec(dev, ["shell", "getprop", prop]).replace('\n', '')
