import serial
import sys
import json
from datetime import datetime
import logging
import logging.handlers as handlers
import os
import time

print("---START RADAR PROGRAM ----")
sys.stdout.flush()

logFolder = "logs"
auto_mounted_usb_root = "/media/pi/"
discover_file = ".find_usb_radar"
# dir_list = os.listdir(auto_mounted_usb_root)
# for root, dirs, files in os.walk(auto_mounted_usb_root):
#   for d in dirs :
#     total_path = os.path.join(os.path.join(auto_mounted_usb_root,d),discover_file)
#     # print ('{0}'.format(total_path))
#     if os.path.exists(total_path):
#       logFolder=os.path.join(auto_mounted_usb_root,d)
#       print('found logfolder {0}',format(logFolder))
#       break

if os.path.exists(os.path.join(auto_mounted_usb_root,discover_file)):
  logFolder=os.path.join(auto_mounted_usb_root)

sys.stdout.flush()
if not os.path.exists(logFolder):
	os.makedirs(logFolder)

print('logging to {0}'.format(logFolder))
sys.stdout.flush()
logger = logging.getLogger('my_app')
logger.setLevel(logging.INFO)
logHandler = handlers.TimedRotatingFileHandler(os.path.join(logFolder,'radar_measurements.log'), when='MIDNIGHT', backupCount=50)
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)


global serial_port

if __name__ == "__main__":
  try:
    serial_port= serial.Serial(
        port="/dev/ttyACM0",
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
        writeTimeout=2
    )
    if  not serial_port.isOpen:
      print ("open serial port")
      serial_port.open()

    
    for x in range(3):
      time.sleep(3)
      serial_port.flushInput()
      serial_port.flushOutput()
      serial_port.write(b'OJ')

      serial_port.write(b'Ot')
      serial_port.write(b'Od')
      serial_port.write(b'OS')
      serial_port.write(b'R>3\r')
      serial_port.write(b'??')

      serial_port.flush()

      received_bytes = serial_port.readall()
      if len(received_bytes) != 0 :
          result = received_bytes.decode()
          print('{0}'.format(result))
      else:
        print("Cannot read settings")

    last_value_time_stamp = datetime.now()
    while (True) :
      # serial_port.write(b'??')
      received_bytes = serial_port.readline()
      if len(received_bytes) != 0 :
        result = received_bytes.decode()
        # print(f"velocity : {result}")
        if "speed" in result:
          j=json.loads(result)
          speed = round(float(j["speed"]))
          now = datetime.now()
          if (now - last_value_time_stamp).microseconds > 500000 :  
            last_value_time_stamp=now
            time_stamp = now.strftime("%d/%m/%Y %H:%M:%S")
            print('{0}:{1}'.format(time_stamp,speed))
            logger.info('{0}:{1}'.format(time_stamp,speed))
            sys.stdout.flush()
      else:
        print(".")

  finally:
    serial_port.close()
