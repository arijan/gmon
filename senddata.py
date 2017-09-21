# coding=utf-8
# gmon
# version 2
# Created in 2017 by Arijan Siska


''' Main table view.
'''

import subprocess
import requests
import time
import datetime
import sys

# helper functions

if 'winver' in dir(sys):  # is this windows system?
    unix = False


    def cleanfields(f):
        rv = []

        for i in f:
            if i != '' and i != '.':
                rv.append(i)

        rv.append(';')
        return rv


    def getipaddress():
        with subprocess.Popen(['ipconfig', '/all'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            gotip = False
            gotether = False

            for line in proc.stdout:
                fields = cleanfields(line.decode('utf-8').rstrip().split(' '))

                if fields[0] == 'Host':
                    hostname = fields[3]

                if not gotip:
                    if fields[0] == 'IPv4':
                        ip = fields[3].rstrip('(Preferred)')

                        if not ip.startswith('127.'):
                            gotip = True

                    if fields[0] == 'Physical':
                        ether = fields[3].replace('-', ':')
                        gotether = True

        return hostname, ether, ip


    def getuptime():
        with subprocess.Popen(['net', 'statistics', 'server'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            for line in proc.stdout:
                fields = cleanfields(line.decode('utf-8').rstrip().split(' '))

                if fields[0] == 'Statistics':
                    uptime = "{} days".format((datetime.datetime.now() - datetime.datetime(int(fields[4]),
                                                                                           int(fields[3].rstrip('.')),
                                                                                           int(fields[2].rstrip(
                                                                                               '.')))).days)

        return uptime


    hostname, macaddr, ipaddr = getipaddress()
    uptime = getuptime()
    miningshell = ['nvmine.bat']

else:  # unix/linux
    unix = True


    def getipaddress():
        with subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE) as proc:
            gotip = False
            gotether = False

            for line in proc.stdout:
                fields = line.decode('utf-8').rstrip().split(' ')

                while fields[0] == '':
                    if len(fields) > 1:
                        fields = fields[1:]
                    else:
                        break

                if not gotip:
                    if fields[0].strip() == 'inet':
                        ip = fields[1]

                        if not ip.startswith('127.'):
                            gotip = True

                if not gotether:
                    if fields[0].strip() == 'ether':
                        ether = fields[1]
                        gotether = True

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
                        return next(fiter) + ' ' + next(fiter)


    hostname = gethostname()
    macaddr, ipaddr = getipaddress()
    miningshell = ['./nvmine.sh']

# main loop

serverurl = 'http://77.234.138.194:8081'
minimumDT = 10

print('Monitoring host {} with mac {} and ip {}'.format(hostname, macaddr, ipaddr))
print('Uptime {}'.format(getuptime()))
t2 = t1 = t0 = int(time.time())

with subprocess.Popen(miningshell, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
    for line in proc.stdout:
        fields = line.decode('utf-8').rstrip().split(' ')

        if len(fields) >= 3:
            if fields[2] == 'm':
                if unix:
                    hashr = int(float(fields[10].rstrip('MH/s')))
                else:
                    hashr = int(float(fields[13]))

                t2 = int(time.time())
                print('dT {}, Hashrate {}, sending:'.format(t2 - t1, hashr), end='')
                t1 = t2

                if t2 - t0 > minimumDT:
                    try:
                        result = requests.post(serverurl, data=dict(Host=hostname, IP=ipaddr,
                                                                    MAC=macaddr, Uptime=getuptime(), Hashrate=hashr,
                                                                    Temp='',
                                                                    Lastseen=int(time.time())))
                        print(result.reason)
                    except:
                        print('Could not connect to server!')
                        pass

                    t0 = t2
                else:
                    print('Pass')
