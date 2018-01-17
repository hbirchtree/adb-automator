from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from sys import argv

device = MonkeyRunner.waitForConnection('', argv[1])
result = device.takeSnapshot()
result.writeToFile(argv[2], 'png')
