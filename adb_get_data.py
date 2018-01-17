#!/usr/bin/python3

from adb_base import *

def adb_get_devices():
    (stdout, stderr), p = adb_exec(["devices"])
    l1 = str(stdout).split('\\n')[1:]
    l = []
    for e in l1:
        if e != "'" and len(e) != 0:
            l = l + [e]
    for i in range(len(l)):
        l[i] = l[i].split('\\t')[0]
    return l


def adb_get_name(dev):
    return "%s %s" % (adb_get_prop(dev, "ro.product.brand"),
                      adb_get_prop(dev, "ro.product.model"))


def adb_get_abis(dev):
    return adb_get_prop(dev, "ro.product.cpu.abilist").split(',')


def adb_get_sdkver(dev):
    return int(adb_get_prop(dev, "ro.build.version.sdk"))


def adb_get_sdkrel(dev):
    return adb_get_prop(dev, "ro.build.version.release")


def adb_get_board(dev):
    return adb_get_prop(dev, "ro.board.platform")


def adb_get_platform(dev):
    return adb_get_prop(dev, "ro.boot.hardware")


def adb_get_product_name(dev):
    return adb_get_prop(dev, "ro.product.name")
