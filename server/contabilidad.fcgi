#!/usr/bin/python
import sys
sys.path.insert(0, '/home/pi/contabilidad/')

from flup.server.fcgi import WSGIServer
from contabilidad import app

if __name__ == '__main__':
    WSGIServer(app).run()
