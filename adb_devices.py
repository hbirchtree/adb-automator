#!/usr/bin/python3

from adb_get_data import *
from os import environ
from os.path import dirname


def print_output(output):
    if len(output) > 0:
        print(output)


class device:
    def __init__(self,dev):
        self.dev = dev
        self.name = adb_get_name(dev)
        self.abi_support = adb_get_abis(dev)
        self.sdk_ver = adb_get_sdkver(dev)
        self.sdk_rel = adb_get_sdkrel(dev)
        self.board = adb_get_board(dev)
        self.platform = adb_get_platform(dev)
        self.product_name = adb_get_product_name(dev)
        self.verbose = False

    def conditional_print(self,log):
        if self.verbose:
            print_output(log)

    def get_identifier(self):
        return "%s (%s, %s, %s)" % (self.name, self.dev, self.sdk_ver, self.platform)

    def execute(self,cmd):
        print(cmd)
        return adb_dev_exec(self.dev, cmd)
        
    def exec_shell(self, cmd):
        print(cmd)
        return adb_dev_exec(self.dev, cmd, True)

    def install_apk(self,file):
        out = self.execute(["install", "-r", file])

    def uninstall_app(self, app):
        out = self.execute(["uninstall", app])

    def is_screen_on(self):
        try:
            state = self.execute(["shell", "dumpsys", "input_method"])
            key = "mInteractive"
            start = state.index(key) + len(key) + 1
            end = state.index("\n", start)
            state = state[start:end]
            print("Screen state: %s" % state)
            return state == "true"
        except ValueError:
            # In this case, we can't find shit
            return False

    def unlock_device(self):
        self.execute(["shell", "input", "keyevent", "26"])
        self.execute(["shell", "input", "keyevent", "82"])

    def lock_device(self):
        self.execute(["shell", "input", "keyevent", "26"])

    def get_screenshot(self,target):
        # try:
        #     # First, try using built-in method. Less dependencies
        #     dev_location = "/sdcard/screenshot.png"
        #     out = self.execute(["shell", "screencap -p %s" % dev_location])
        #     self.conditional_print(out)
        #     out = self.execute(["pull", dev_location,target])
        #     self.conditional_print(out)
        #     out = self.execute(["shell", "rm %s" % dev_location])
        #     self.conditional_print(out)
        # except RuntimeError:
        # In case it's an ancient device, fall back to Monkeyrunner
        monkeyrun("monkey_screenshot.py", [self.dev, target])
        return None

    def display_logcat(self):
        adb_dev_exec(self.dev, ["logcat"], live_output=True)

    def get_installed_packages(self):
        out = self.execute(["shell", "pm list packages"]).split('\n')
        for i in range(len(out)):
            out[i] = out[i][8:]
        out.remove('')
        return out

    def get_app_activity(self, pkg):
        launcher = ""
        pkg_desc = self.execute(["shell", "pm dump %s" % pkg]).split('\n')
        for i in range(len(pkg_desc)):
            if pkg_desc[i].strip().startswith('android.intent.action.MAIN'):
                launcher = pkg_desc[i+1].strip().split(" ")[1]
                break
        return launcher
        
    def pidof_activity(self, pkg):
        outp = self.execute(["shell",
                "ps -A | grep '%s'" % pkg])            
        if len(outp) != 0:
            pslist = [e for e in outp.split(" ") if len(e) > 0]
            return int(pslist[1])
        
        outp = self.execute(["shell", "ps | grep '%s'" % pkg])
        
        if len(outp) != 0:
            pslist = [e for e in outp.split(" ") if len(e) > 0]
            return int(pslist[1])
        else:
            return -1
            
    def isaof_activity(self,  pkg):
        outp = self.execute(["shell",
            "pm dump %s | grep 'instructionSet'" % pkg])
        
        if len(outp) != 0:
            outp = outp[outp.find('instructionSet='):]
            outp = outp[len('instructionSet='):].replace('\n', '').strip()
            return outp
        else:
            return "arm"
            
    def nlpof_activity(self, pkg):
        outp = self.execute(["shell",
            "pm dump %s | grep 'NativeLib'" % pkg])
        
        if len(outp) != 0:
            outp = outp[outp.find('=') + 1:].replace('\n', '')
            return '%s/%s' % (outp, self.isaof_activity(pkg))
        else:
            return "/data/data/%s/lib/%s" \
                % (pkg, self.isaof_activity(pkg))

    def launch_app(self,pkg, extra_args=""):
        # Before launching, unlock the device
        if not self.is_screen_on():
            self.unlock_device()

        launcher = self.get_app_activity(pkg)
        if len(launcher) > 0:
            self.conditional_print("Launching %s -> %s" % (pkg, launcher))
            out = self.execute(["shell","am start %s -a %s -n %s --es 'COFFEE_REPORT_URL' '%s'"
                               % (extra_args, pkg, launcher, 'abc')])
            print_output(out)
        else:
            self.conditional_print("Failed to launch application, could not find intent")

    def stop_app(self, pkg):
        try:
            stop_msg = self.execute(["shell", "am", "force-stop", pkg])
            if "Error" in stop_msg:
                raise RuntimeError()
        except RuntimeError:
            pid = self.pidof_activity(pkg)
            try:
                print_output(self.execute(["shell",  "kill", pid]))
            except IndexError:
                pass
        # Lock device afterwards
        #self.lock_device()


def get_num_devices():
    return len(adb_get_devices())


def get_dev(uuid):
    try:
        if uuid not in adb_get_devices():
            raise IndexError()
        return device(uuid)
    except IndexError:
        return None
