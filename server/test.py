

import zerorpc
import os,sys
c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")

print c.append('123456789','hello')
