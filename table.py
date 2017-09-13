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
    return '{} days'.format(x)

def timediffconvert(x):
    return '{} s'.format(int(time.time()) - int(x))

tablehtmlfilename = ''
tabledata = dict(columns=['Host', 'IP', 'MAC', 'Uptime', 'Hashrate', 'Temp', 'Lastseen'], rows={})
tabledatarepresentation = dict()
tabledataconverters = dict(Host=identity, IP=identity, MAC=identity, Uptime=uptimeconvert, Hashrate=identity,
                           Temp=identity, Lastseen=timediffconvert)

@globalpathrouter.addroute(path=tablehtmlfilename, secure=True)
def table(environ):
    for item in tabledata['rows'].values():
        newitem = dict()

        for k, v in item.items():
            newitem[k] = tabledataconverters[k](v)

        tabledatarepresentation[newitem['Host']] = newitem

    htmldocument = dominate.document('Table')

    with htmldocument.head:
        createhtmlhead(tablecssfilename)
        tag.meta(http_equiv='refresh', content='60; url="' + generalsiteprefix + tablehtmlfilename + '"')
        tag.script(src=tablejsfilename, type=TEXTJAVASCRIPT)

    with htmldocument.body:
        with tag.div(cls='main'):
            tag.h1('Main table view')
            createsimpletable(tabledatarepresentation, tabledata['columns'], tabledata['columns'], id='hosttable')

    return htmldocument

@globalpathrouter.addroute(path=tablehtmlfilename, method=POSTMETH)
def tablepost(environ):
    decoded = decodeenviron(environ)

    line = {}

    for col in tabledata['columns']:
        if col in decoded:
            line[col] = decoded[col][0]
        else:
            line[col] = ''

    tabledata['rows'][line['Host']] = line
