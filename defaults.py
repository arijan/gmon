# coding=utf-8
# gmon
# version 2
# Created in 2017 by Arijan Siska


import os
import json
from datetime import datetime
import dominate

tag = dominate.tags
dominate.tags.raw = dominate.util.raw
from urllib.parse import parse_qs
from http.cookies import SimpleCookie


# html ctypes

TEXTHTML = 'text/html'
TEXTCSS = 'text/css'
IMAGEJPEG = 'image/jpeg'
IMAGEPNG = 'image/png'
TEXTJAVASCRIPT = 'text/javascript'
APPLICATIONPDF = 'application/pdf'

allctypes = (TEXTHTML, TEXTCSS, IMAGEJPEG, IMAGEPNG, TEXTJAVASCRIPT, APPLICATIONPDF)

# http request methods

GETMETH = 'GET'
POSTMETH = 'POST'
allmethods = (GETMETH, POSTMETH)

# path router

generalsiteprefix = "/"


class pathaction():
    def __init__(self, ctype=None, secure=False, htmlgeneratingfunc=None, postfunctions=None, endtime=None):
        self.ctype = ctype
        self.secure = secure
        self.htmlgeneratingfunc = htmlgeneratingfunc
        self.postfunctions = postfunctions if postfunctions else []
        self.endtime = endtime

    def __str__(self):
        return ', '.join(['ctype=' + self.ctype,
                          'secure=' + str(self.secure),
                          'htmlgeneratingfunc=' + self.htmlgeneratingfunc.__name__,
                          'postfunctions=[' + ', '.join(f.__name__ for f in self.postfunctions) + ']',
                          'endtime=' + str(self.endtime)])


class pathrouter():
    def __init__(self):
        self.paths = {}
        self.menuitems = {'all': []}

    def addroute(self, path=None, method=GETMETH, ctype=TEXTHTML, secure=False, name='',
                 postfunctions=None, endtime=None):
        path = '/' + path

        if type(path) is not str:
            raise ValueError('Pathrouter got illegal path: ' + str(path))

        if method not in allmethods:
            raise ValueError('Pathrouter got illegal method: ' + str(method))

        if ctype not in allctypes:
            raise ValueError('Pathrouter got illegal ctype: ' + str(ctype))

        if secure not in (True, False):
            raise ValueError('Pathrouter got illegal security: ' + str(secure))

        if endtime:
            if type(endtime) is not datetime:
                raise ValueError('Pathrouter got illegal endtime: ' + str(endtime))

        def routedecorator(htmlgeneratingfunc):
            self.paths[(path, method)] = pathaction(ctype=ctype, secure=secure, htmlgeneratingfunc=htmlgeneratingfunc,
                                                    postfunctions=postfunctions, endtime=endtime)
            return htmlgeneratingfunc

        return routedecorator

    def getpathaction(self, pathmethodtuple):
        return self.paths[pathmethodtuple]

    def getpaths(self):
        return self.paths.items()


# important instance... to decorate all individual page generating functions

globalpathrouter = pathrouter()

# login

logincookiename = 'loggedinuser'
lastpagevisitedname = 'lastpagevisited'


# helper functions for file load & save

def getDirectory(direct):
    return os.listdir(direct)


def getLastfile(direct):
    return sorted(getDirectory(direct))[-1]


def loadFile(direct, f):
    ff = os.path.join(direct, f)

    with open(ff, 'rb') as fd:
        ret = fd.read()

    return ret


def loadJson(direct, f):
    ff = os.path.join(direct, f)

    with open(ff, 'r', encoding='utf-8') as fd:
        ret = json.load(fd)

    if type(ret) is dict:
        ret['filename'] = f

    return ret


def saveJson(direct, obj, savefilenameinobj=False):
    filename = str(datetime.utcnow().timestamp())
    filenamewithpath = os.path.join(direct, filename)
    print('Saved JSON ' + filename + ' in ' + direct)

    if savefilenameinobj:
        if type(obj) is dict:
            obj['filename'] = filename

    with open(filenamewithpath, 'w', encoding='utf-8') as fd:
        json.dump(obj, fd, indent=4, ensure_ascii=False)


def deleteJson(direct, obj):
    if type(obj) is dict:
        if 'filename' in obj:
            print('File: ' + obj['filename'] + ' in: ' + direct + ' deleted fast.')
            os.remove(os.path.join(direct, obj['filename']))
            return

    for filename in getDirectory(direct):
        jsonobject = loadJson(direct, filename)

        if obj == jsonobject:
            print('File: ' + filename + ' in: ' + direct + ' deleted slow.')
            os.remove(os.path.join(direct, filename))


# cookie helper functions

def getcookievaluefromenv(environ, cookiename):
    if 'HTTP_COOKIE' in environ:
        cookie = SimpleCookie(environ['HTTP_COOKIE'])

        if cookiename in cookie:
            return cookie[cookiename].value

    return None


def decodeenviron(environ):
    return environ['parsedwsgiinput']


# html helper functions

class escapetag:
    def __init__(self, tagname, *args, **kwargs):
        self.tagname = tagname
        self.args = args
        self.kwargs = {}

        for k, v in kwargs.items():
            if v:  # we only need to add key, value pair if value: is not False
                self.kwargs[k] = v

    def __call__(self):
        return getattr(tag, self.tagname)(*self.args, **self.kwargs)


globalJS = 'global.js'


@globalpathrouter.addroute(path=globalJS)
def globaljavascript(environ):
    return loadFile('.', globalJS)


hidecolumn = 'hideThisColumn(this)'
unhideall = 'unhideAllColumns(this)'
sortbycolumn = 'sortByColumn(this)'
filterbycolumn = 'filterByColumn(this)'


def createsimpletable(collectionofdicts, fields, representation, cls=None, id=None, headerbuttons=True, linenumbers=True,
                      editfields=None):
    table = tag.table()

    if cls:
        table['cls'] = cls

    if id:
        table['id'] = id

    if not editfields:
        editfields = [False for x in fields]

    counter = 1

    with table:
        with tag.tbody():
            with tag.tr():
                tag.th(tag.p(
                    tag.button('↶\n•', type='button', cls='tablebutton', onClick=unhideall)) if headerbuttons else '')

                for i, f in enumerate(representation):
                    index = i + 1

                    if type(f) is str:
                        if len(f) == 0:
                            tag.th('')
                        elif f[-1] == '.' or headerbuttons == False:
                            tag.th(f)
                        else:
                            tag.th(f, tag.p(
                                tag.button('•', type='button', cls='tablebutton', column=index, onClick=hidecolumn),
                                tag.button('⇵', type='button', cls='tablebutton', column=index, onClick=sortbycolumn),
                                tag.input(placeholder='filter', cls='tablefilter', column=index, onkeyup=filterbycolumn,
                                          value=''),
                                cls='tablebuttons'))
                    elif type(f) is escapetag:
                        if headerbuttons:
                            tag.th(f(), tag.p(
                                tag.button('•', type='button', cls='tablebutton', column=index, onClick=hidecolumn),
                                tag.button('⇵', type='button', cls='tablebutton', column=index, onClick=sortbycolumn),
                                tag.input(placeholder='filter', cls='tablefilter', column=index, onkeyup=filterbycolumn,
                                          value=''),
                                cls='tablebuttons'))
                        else:
                            tag.th(f())


            for r in collectionofdicts if type(collectionofdicts) is list else collectionofdicts.values():
                with tag.tr():
                    tag.td(tag.span(str(counter), id=id + str(counter) if id else '') if linenumbers else '')
                    counter += 1

                    for f, e in zip(fields, editfields):
                        tag.td(r[f]() if callable(r[f]) else r[f], cls='simpletable_' + str(f),
                               contenteditable="true" if e else "false")


# html elements

faviconname = 'favicon.png'
favicontype = IMAGEPNG

@globalpathrouter.addroute(path=faviconname, ctype=favicontype)
def globaljavascript(environ):
    return loadFile('.', faviconname)

def createhtmlhead(cssname):
    tag.meta(http_equiv='Content-Type', content=TEXTHTML + '; charset=utf-8')
    tag.link(href=generalsiteprefix + cssname, rel='stylesheet', type=TEXTCSS, media='all')
    tag.link(href=generalsiteprefix + faviconname, rel='icon', type=favicontype)
