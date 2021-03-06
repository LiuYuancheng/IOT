#!/usr/bin/python
# -----------------------------------------------------------------------------
# Name:        qtPain.py
#
# Purpose:     find the com port information.
#
# Author:      Yuancheng Liu
#
# Created:     2019/04/17
# Copyright:   YC
# License:     YC
# -----------------------------------------------------------------------------
import sys
import glob
import serial
from datetime import datetime

def serial_ports():
    """ Lists used serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        # Check whether the port can be open. 
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    # Log the reasult into the log file. 
    now = datetime.now()
    timeStr = now.strftime("%m_%d_%H_%M")
    logName = ''.join(("CommLog", timeStr, '.txt'))
    with open(logName, 'at') as f:
        print(now.strftime("%m/%d/%Y, %H:%M:%S  ") + str(result), file = f)
    return result

if __name__ == '__main__':
    print(serial_ports())