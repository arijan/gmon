# coding=utf-8
# wsgiapp
# version 2
# Created in 2017 by Arijan Siska

''' login stuff
'''

import dominate

tag = dominate.tags
dominate.tags.raw = dominate.util.raw

from http.cookies import SimpleCookie
from random import randint
from hashlib import sha512
from defaults import *


# get user database

userdatabasefilename = 'userdatabase.json'
userdatabase = loadJson('.', userdatabasefilename)
del (userdatabase['filename'])
print('All users:', len(userdatabase))


# helper functions for login

def getrandomdigits(n):
    # return ('{:0' + str((n - 1) // 3 + n) + '_d}').format(randint(0, 10**n - 1)).replace('_', ' ')
    randominteger = randint(0, 10 ** n - 1)
    return ' '.join([('{:0' + str(n) + 'd}').format(randominteger)[i: i + 3] for i in range(0, n, 3)])


def passwordhashgenerate(username, password):
    salt = getrandomdigits(39)
    myhash = sha512(bytes(password.replace(' ', '') + salt, 'utf-8')).hexdigest()
    return {username.lower(): dict(salt=salt, sha512=myhash)}


def passwordhashcheck(username, password):
    username = username.strip().lower()
    password = password.strip().replace(' ', '')

    if username in userdatabase:
        if sha512(bytes(password + userdatabase[username]['salt'], 'utf-8')).hexdigest() == userdatabase[username][
            'sha512']:
            return True
        else:
            return False
    else:
        return False


def getuserfromenv(environ):
    token = getcookievaluefromenv(environ, logincookiename)

    if token:
        return getuserfromtoken(token)
    else:
        return None


def getuserfromtoken(token):
    for u, item in userdatabase.items():
        if 'token' in item:
            if item['token'] == token:
                return u
    else:
        return None


logincssfilename = 'default.css'

@globalpathrouter.addroute(path=logincssfilename, ctype=TEXTCSS)
def getlogincss(environ):
    return loadFile('.', logincssfilename)


loginhtmlfilename = 'login.html'


@globalpathrouter.addroute(path=loginhtmlfilename)
def login(environ):

    htmldocument = dominate.document('Login')

    with htmldocument.head:
        createhtmlhead(logincssfilename)

    with htmldocument.body:
        main = tag.div(cls='main')

        with main:
            tag.h3('Please enter:')
            with tag.form(action=loginhtmlfilename, method='post'):
                with tag.table():
                    with tag.tbody():
                        with tag.tr():
                            tag.td('Username:')
                            with tag.td():
                                tag.input(type='text', name='user', cls='longtextinput')
                        with tag.tr():
                            tag.td('Password:')
                            with tag.td():
                                tag.input(type='password', name='password', cls='longtextinput')
                tag.input(type='submit', value='Login')

    return htmldocument


@globalpathrouter.addroute(path=loginhtmlfilename, method=POSTMETH)
def loginpost(environ):
    decoded = decodeenviron(environ)

    if decoded:
        if 'user' in decoded and 'password' in decoded:
            username = decoded['user'][0].lower()
            password = decoded['password'][0]

            if username in userdatabase:
                if passwordhashcheck(username,
                                     password):  # if passwork is ok add cookie to browser and token to tokendatabase
                    path = getcookievaluefromenv(environ, lastpagevisitedname)

                    if not path:
                        path = "/"

                    htmldocument = dominate.document('Login')

                    with htmldocument.head:
                        createhtmlhead(logincssfilename)
                        tag.meta(http_equiv='refresh', content='2; url="' + path + '"')

                    with htmldocument.body:
                        tag.p('Logged in ' + username + '.')

                    cookie = SimpleCookie()
                    token = getrandomdigits(30)
                    userdatabase[username]['token'] = cookie[logincookiename] = token
                    cookie[logincookiename]['max-age'] = 86400
                    print('User "' + username + '" logged in.')
                    return htmldocument, ('Set-Cookie', cookie[logincookiename].OutputString())

    htmldocument = dominate.document('Login')

    with htmldocument.head:
        createhtmlhead(logincssfilename)
        tag.meta(http_equiv='refresh', content='2; url=' + loginhtmlfilename)

    with htmldocument.body:
        tag.p('Wrong user or password!', cls='alert')

    print('User login error!')
    return htmldocument


logouthtmlfilename = 'logout.html'


@globalpathrouter.addroute(path=logouthtmlfilename)
def logout(environ):
    user = getuserfromenv(environ)

    if user:
        if user in userdatabase:
            if 'token' in userdatabase[user]:
                del userdatabase[user]['token']

    user = 'Anonymous'

    htmldocument = dominate.document('Logout')

    with htmldocument.head:
        createhtmlhead(logincssfilename)
        tag.meta(http_equiv='refresh', content='2; url="/"')

    with htmldocument.body:
        tag.p('Logged out.')

    cookie = SimpleCookie()
    cookie[logincookiename] = 'Anonymous'
    cookie[logincookiename]['max-age'] = -1
    print('User "' + user + '" logged out.')
    return htmldocument, ('Set-Cookie', cookie[logincookiename].OutputString())