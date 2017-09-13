# coding=utf-8
# gmon
# version 2
# Created in 2017 by Arijan Siska

''' A relatively simple WSGI application.
'''

import time
from datetime import datetime
from http.cookies import SimpleCookie
from defaults import *

# import all the individual pages

import login
import table


# main application processing loop

def default_app(environ, start_response):
    clockstart = time.time()

    if 'REQUEST_METHOD' in environ:
        reqmethod = environ['REQUEST_METHOD']
    else:
        reqmethod = 'GET'

    if 'PATH_INFO' in environ:
        path = environ['PATH_INFO']
    else:
        path = '/'

    environ['parsedwsgiinput'] = {}

    if 'CONTENT_LENGTH' in environ and 'wsgi.input' in environ:
        e = environ.get('CONTENT_LENGTH', '0')

        if e != '':
            length = int(e)

            if length > 0:
                body = parse_qs(str(environ['wsgi.input'].read(length), 'utf-8'))
                print('Post request: ', body)
                environ['parsedwsgiinput'] = body if body else {}

    pathkey = (path, reqmethod)
    user = login.getuserfromenv(environ)
    headers = [('Content-type', 'text/html; charset=utf-8')]
    print(time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime()) + ' user:' + str(user) + ' req:' + str(pathkey))

    if pathkey in globalpathrouter.paths:  # we have a hit on path
        pathvalue = globalpathrouter.getpathaction(pathkey)

        if pathvalue.endtime:
            if pathvalue.endtime < datetime.now():
                headers = [('Content-type', 'text/html; charset=utf-8')]
                start_response('200 OK', headers)
                return [b'Access closed.']

        if pathvalue.secure == False or user:
            # if no security required
            # or user logged in we serve content
            headers = [('Content-type', pathvalue.ctype + '; charset=utf-8')]
            htmlpage = pathvalue.htmlgeneratingfunc(environ)

            if pathvalue.postfunctions:  # execute all post functions
                for f in pathvalue.postfunctions:
                    f(environ, htmlpage)

            if type(htmlpage) is tuple:  # if page returns cookie headers with html, we separate those
                htmlpage, cookieheaders = htmlpage
                headers.append(cookieheaders)

            if type(htmlpage) is not bytes:
                htmlpage = bytes(str(htmlpage), 'utf-8')

            start_response('200 OK', headers)
            print('ResponseIn: {:.6f}s'.format(time.time() - clockstart))
            return [htmlpage]
        else:
            headers.append(('Location', login.loginhtmlfilename))
            cookie = SimpleCookie()
            lastpagevisited = path
            cookie[lastpagevisitedname] = lastpagevisited  # set lastpagevisited cookie to current path
            cookie[lastpagevisitedname]['max-age'] = 60  # we store this cookie for maximum of 1 minute
            headers.append(('Set-Cookie', cookie[lastpagevisitedname].OutputString()))
            start_response('302 Found', headers)  # if user is not allowed, we redirect to login
            return [b'Not authorized. Please log in.']
    else:
        start_response('404 Not found', headers)  # if no page is found in pathrouter...
        return [b'Resource not found.']


# print all routes

print('All server routes:')

for a, b in globalpathrouter.getpaths():
    print(a, '->', b)

# if running directly create a reference server and start serving

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    httpd = make_server('', 8081, default_app)
    print("Serving...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('...break received, shutting down the web server.')
        del (httpd)