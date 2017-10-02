# coding=utf-8
# gmon
# version 2
# Created in 2017 by Arijan Siska


''' Main table view.
'''

import dominate

tag = dominate.tags
dominate.tags.raw = dominate.util.raw

import time
import os
import subprocess
import json
import codecs
from defaults import *


# url serving functions

tablecssfilename = 'default.css'

@globalpathrouter.addroute(path=tablecssfilename, ctype=TEXTCSS)
def gettablecss(environ):
    return loadFile('.', tablecssfilename)

tablejsfilename = 'table.js'

@globalpathrouter.addroute(path=tablejsfilename, ctype=TEXTJAVASCRIPT)
def gettablejs(environ):
    return loadFile('.', tablejsfilename)

def identity(x):
    return x

def uptimeconvert(x):
    return '{}'.format(x)

def timediffconvert(x):
    try:
        ix = int(x)
    except: ValueError
        ix = int(time.time())

    return '{} s'.format(int(time.time()) - ix)

def getgraph(x):
    # get rrd data
    retval = ''
    rrdfile = os.path.join(rrdoutputdir, x + '.rrd')
    result = []

    try:
        with subprocess.Popen(['rrdtool', 'xport', 'DEF:h=' + rrdfile + ':h:AVERAGE', 'XPORT:h', '--end', 'now-60s',
                               '--start', 'now-1860s', '--json'], stdout=subprocess.PIPE) as proc:
            reader = codecs.getreader('utf-8')
            result = json.load(reader(proc.stdout))

        vmax = max([x[0] if x[0] else 0 for x in result['data']])
        vmin = min([x[0] if x[0] else vmax for x in result['data']])
        vdiff = vmax - vmin

        if vdiff == 0:
            vdiff = 1

        rrddata = [x[0] if x[0] else vmin for x in result['data']]
        retval = 'T:{:.0f} B:{:.0f} '.format(vmax, vmin) + ''.join([barchars[round((x - vmin) * barcharslen / vdiff)] for x in rrddata])
    except:
        print(result)

    return retval

tablehtmlfilename = ''
tabledata = dict(columns=['Host', 'IP', 'MAC', 'Uptime', 'Hashrate', 'Temp', 'Lastseen', 'Graph'], rows={})
tabledatarepresentation = dict()
tabledataconverters = dict(Host=identity, IP=identity, MAC=identity, Uptime=uptimeconvert, Hashrate=identity,
                           Temp=identity, Lastseen=timediffconvert, Graph=getgraph)
barchars = list('▁▂▃▄▅▆▇█')
barcharslen = len(barchars) - 1

@globalpathrouter.addroute(path=tablehtmlfilename, secure=True)
def table(environ):
    # for all data rows
    for item in tabledata['rows'].values():
        newitem = dict()

        # get table data
        for k, v in item.items():
            newitem[k] = tabledataconverters[k](v)

        # represent data
        tabledatarepresentation[newitem['Host']] = newitem

    # create html
    htmldocument = dominate.document('Table')

    with htmldocument.head:
        createhtmlhead(tablecssfilename)
        tag.meta(http_equiv='refresh', content='60; url=' + generalsiteprefix + tablehtmlfilename)
        tag.script(src=tablejsfilename, type=TEXTJAVASCRIPT)

    with htmldocument.body:
        with tag.div(cls='main'):
            tag.h1('Main table view')
            createsimpletable(tabledatarepresentation, tabledata['columns'], tabledata['columns'], id='hosttable')

    return htmldocument

rrdoutputdir = 'rrds'

@globalpathrouter.addroute(path=tablehtmlfilename, method=POSTMETH)
def tablepost(environ):
    # get html post data
    decoded = decodeenviron(environ)

    line = {}

    for col in tabledata['columns']:
        if col in decoded:
            line[col] = decoded[col][0]
        else:
            line[col] = ''

    # fill in missing required data
    if line['Host'] == '':
        if line['MAC'] != '':
            line['Host'] = line['MAC']
        else:
            line['Host'] = 'Unknown'

    line['Graph'] = line['Host']

    # enter data into the table
    tabledata['rows'][line['Host']] = line

    # save data into rrd database
    rrdfile = os.path.join(rrdoutputdir, line['Host'] + '.rrd')

    if os.path.isfile(rrdfile):
        pass
    else:
        print('create rrd for {}'.format(line['Host']))

        try:
            result = subprocess.run(
                ['rrdtool', 'create', rrdfile, 'DS:h:GAUGE:60:U:U', 'RRA:AVERAGE:0.5:1:120',
                 'RRA:AVERAGE:0.5:60:8640', '--start=now-1y', '--step=60'])
        except:
            print(result)

    try:
        result = subprocess.run(
            ['rrdtool', 'update', rrdfile, '{}:{}'.format(line['Lastseen'], line['Hashrate'])])
    except:
        print(result)

    return ''
