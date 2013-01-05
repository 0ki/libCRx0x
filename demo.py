#!/usr/bin/env python2
# Program for testing libCRx0x
#
# Copyright Kirils Solovjovs, 2013
import libCRx0x as cr
device = cr.crx('/dev/ttyUSB0',True)

print "Device Model: " + device.getModel()[1]
print "Device Node: " + device.getNode()
print device.beep(0.1)
print device.setAntenna(1)
print device.setLED(1)

device.close()

