# libCRx0x.py
#
# Python library for accessing CRx0x 13.54MHz RFID readers
#
# Copyright Kirils Solovjovs, 2013

# I have written a 300-line PHP blob that implements the protocol and I am gonna convert it to clean python implementation over time.

import serial
import binascii
import time
import struct

class crx:
  def __init__(self, port, safetywarnings=False):
    # open port
    self.__safetywarnings=safetywarnings
    self.__s = serial.Serial(port, 19200)
    self.speed(19200)

  def __exit__(self, type, value, traceback):
    self.close()

  def close(self):
    self.setAntenna(0)
    self.setLED(0)
    self.__s.close
  
  def speed(self,speed):
    if(speed==4800): speed=0
    elif(speed==9600): speed=1
    elif(speed==14400): speed=2
    elif(speed==19200): speed=3
    elif(speed==28800): speed=4
    elif(speed==38400): speed=5
    elif(speed==57600): speed=6
    elif(speed==115200): speed=7
    else: return False
    return self.__sendCommand('\x01\x01'+chr(speed))

  def __sendCommand(self,data):
    self.__s.write(self.__buildCommand(data))
    time.sleep(.1)
    an = ""
    leng = 99999
    self.__expect('\xaa\xbb')

 # need to strip aa00 another way - later on 
    while (leng > len(an)):
      an += self.__s.read()
      try:
        leng=ord(an[0])+ord((an[2] if (an[0]==0xaa and an[1]==0x0) else an[1]))*0x100 + an.count('\xaa\x00')+2
      except IndexError:
        pass

    return self.__dismantleResponse(an,data[:2])

  def __buildCommand(self,data):
    command=struct.pack('<H', len(data)+3)+'\x00\x00'+data
    xo=0
    for char in command[2:]:
      xo = xo ^ ord(char)
    command += chr(xo)
    command = command.replace('\xaa','\xaa\x00')
    command = '\xaa\xbb' + command
    return command

  def __dismantleResponse(self,data,expCommand):
    xo=0
    data=data.replace('\xaa\x00','\xaa')
    for char in data[2:]:
      xo = xo ^ ord(char)
    stat=ord(data[6:7])
    if (xo or expCommand[0:2] != data[4:6]):
      print binascii.hexlify(data)
      raise Exception("communication error, CRC="+str(xo))
    data=data[7:-1]
    if len(data)==0:
      if stat == 0:
        return True
      else:
        return stat
    else:
      return [stat,data]

  def __expect(self, stri,nonfatal=False):
    a = self.__s.read(len(stri))
    if nonfatal:
      return (a == stri)
    if (a != stri):
      raise Exception("communication error; expected [" + binascii.hexlify(stri) + "] got [" + binascii.hexlify(a) + "]")

  def __warn(self):
    if(self.__safetywarnings):
      print "WARNING! NEXT SWIPE WILL WRITE TO CARD WITH "+ ("HIGH" if self.getCo() else "LOW") + " COERCIVITY"

  def getModel(self):
    return self.__sendCommand('\x04\x01')

  def getNode(self):
    node=self.__sendCommand('\x03\x01')
    if node[0]:
      return False
    else:
      return binascii.hexlify(node[1])

  def setAntenna(self,on):
    return self.__sendCommand('\x0c\x01'+ ('\x01' if on else '\x00'))

  def setLED(self,bits): # R3 Y2 G1
    if ( bits not in [0,1,2,4,5]):
      raise Exception("Hardware does not have this led");
    if ( bits == 5 or bits == 2): return self.__sendCommand('\x07\x01\x03')
    if ( bits == 0 ): return self.__sendCommand('\x07\x01\x00')
    if ( bits == 4 ): return self.__sendCommand('\x07\x01\x01')
    if ( bits == 1 ): return self.__sendCommand('\x07\x01\x02')

  def beep(self,delay):
    delay=int(delay/0.01)
    if(delay<0): delay=0
    if(delay>255): delay=255
    return self.__sendCommand('\x06\x01'+chr(delay))


