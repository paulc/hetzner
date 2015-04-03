
from __future__ import print_function

import socket,time

def up(host,port,logf=None):
    while True:
        try:
            s = socket.create_connection((host,port),timeout=5)
            s.close()
            time.sleep(5)
            if logf:
                logf()
        except (socket.timeout,socket.error):
            return

def poll(host,port,timeout=60,logf=None):
    now = time.time()
    while time.time() < now + timeout:
        try:
            s = socket.create_connection((host,port),timeout=5)
            s.close()
            return True
        except (socket.timeout,socket.error):
            if logf:
                logf()
            time.sleep(5)
    return False
