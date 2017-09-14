# coding=utf-8
# gmon
# version 2
# Created in 2017 by Arijan Siska


''' Main table view.
'''

import subprocess
import requests
import time


# helper functions

def getipaddress():
    with subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE) as proc:
        gotip = False
        gotether = False

        for line in proc.stdout:
            fields = line.decode('utf-8').rstrip().split(' ')

            if not gotip:
                if fields[0].strip() == 'inet':
                    ip = fields[1]

                    if not ip.startswith('127.'):
                        gotip = True

            if not gotether:
                if fields[0].strip() == 'ether':
                    ether = fields[1]
                    gotether = True

            if gotether and gotip:
                return ether, ip

    return None

def gethostname():
    with subprocess.Popen(['hostname'], stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            return line.decode('utf-8').rstrip()

def getuptime():
    with subprocess.Popen(['uptime'], stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            fields = line.decode('utf-8').rstrip().split(' ')
            fiter = iter(fields)

            for f in fiter:
                if f == 'up':
                    return next(fiter)

# main loop

hostname = gethostname()
macaddr, ipaddr = getipaddress()
print('Monitoring host {} with mac {} and ip {}'.format(hostname, macaddr, ipaddr))
print('Uptime {}'.format(getuptime()))
t2 = t1 = int(time.time())

with subprocess.Popen(['cat', 'testdata.txt'], stdout=subprocess.PIPE) as proc:
    for line in proc.stdout:
        fields = line.decode('utf-8').rstrip().split(' ')

        if fields[2] == 'm':
            hashr = int(float(fields[10].rstrip('MH/s')))
            t2 = int(time.time())
            print('dT {}, Hashrate {}, sending:'.format(t2 - t1, hashr), end='')
            t1 = t2

            try:
                result = requests.post('http://localhost:8081', data=dict(Host=hostname, IP=ipaddr,
                                        MAC=macaddr, Uptime=getuptime(), Hashrate=hashr, Temp='',
                                        Lastseen=int(time.time())))
            except:
                pass

            print(result.reason)

        time.sleep(5)