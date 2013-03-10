#coding=utf-8

import time
import urllib2
import urllib
import cookielib
import re
import json
import hashlib
import base64
import os

import lxml.html as HTML
from log import logger

from settings import (
    account,
    pwd,
)

cookie_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cookies.txt')
def create_cookie_file():
    if not os.path.exists(cookie_file):
        f = open(cookie_file, 'w')
        try:
            return True
        finally:
            f.close()
    return False


def urldecode(link):
    decodes = {}
    if '?' in link:
        params = link.split('?')[1]
        for param in params.split('&'):
            k, v = tuple(param.split('='))
            decodes[k] = urllib.unquote(v)
    return decodes

class Fetcher(object):
    def __init__(self):
        self.create = create_cookie_file()
        self.cj = cookielib.LWPCookieJar()
        if not self.create:
            self.cj.load(cookie_file)
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(self.cookie_processor, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)

        self.username = account
        self.pwd = pwd

    def get_servertime(self):
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&client=ssologin.js(v1.3.18)&_=1329806375939'
        data = urllib2.urlopen(url).read()
        regex = re.compile('\((.*)\)')
        try:
            json_data = regex.search(data).group(1)
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            return servertime, nonce
        except:
            print 'Get servertime error!'

    def get_pwd(self, pwd, servertime, nonce):
        sha1 = lambda pwd: hashlib.sha1(pwd).hexdigest()
        for _ in range(2):
            pwd = sha1(pwd)
        pwd = pwd + servertime + nonce
        return sha1(pwd)

    def get_user(self, username):
        username = urllib.quote(username)
        return base64.encodestring(username)[:-1]

    def login(self):
        assert self.username is not None and self.pwd is not None

        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
        try:
            servertime, nonce = self.get_servertime()
        except:
            return
        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': self.get_user(self.username),
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'wsse',
            'sp': self.get_pwd(self.pwd, servertime, nonce),
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        postdata = urllib.urlencode(postdata)
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
        req = urllib2.Request(url, postdata, headers)
        text = urllib2.urlopen(req).read()
        regex = re.compile('location\.replace\(\'(.*?)\'\)')
        try:
            login_url = regex.search(text).group(1)
            logger.info(login_url)
            urllib2.urlopen(login_url)
            logger.info("login succeed!")
        except:
            logger.info("login failed!")

    def fetch(self, url):
        return urllib2.urlopen(url).read()

class CnFetcher(Fetcher):
    def __init__(self):
        super(CnFetcher, self).__init__()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}

    def _get_rand(self, url):
        headers = {'User-Agent':'Mozilla/5.0 (Windows;U;Windows NT 5.1;zh-CN;rv:1.9.2.9)Gecko/20100824 Firefox/3.6.9',
                   'Referer':''}
        req = urllib2.Request(url ,urllib.urlencode({}), headers)
        resp = urllib2.urlopen(req)
        login_page = resp.read()
        rand = HTML.fromstring(login_page).xpath("//form/@action")[0]
        passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
        vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
        return rand, passwd, vk

    def get_rand(self, url):
        error = None
        for i in range(3):
            try:
                return self._get_rand(url)
            except urllib2.httplib.BadStatusLine, e:
                error = e
                time.sleep((i + 1) * 10)
                continue
        if error is not None:
            raise error

    def login(self):
        assert self.username is not None and self.pwd is not None

        def _urlopen(req):
            for i in range(3):
                try:
                    return urllib2.urlopen(req)
                except urllib2.httplib.BadStatusLine, e:
                    if i < 2:
                        time.sleep((i + 1) * 10)
                        continue
                    else:
                        raise e

        url = 'http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='
        rand, passwd, vk = self.get_rand(url)
        data = urllib.urlencode({'mobile': self.username,
                                 passwd: self.pwd,
                                 'remember': 'on',
                                 'backURL': 'http://weibo.cn/',
                                 'backTitle': '新浪微博',
                                 'vk': vk,
                                 'submit': '登录',
                                 'encoding': 'utf-8'})
        url = 'http://3g.sina.com.cn/prog/wapsite/sso/' + rand
        req = urllib2.Request(url, data, self.headers)
        # resp = urllib2.urlopen(req)
        resp = _urlopen(req)
        page = resp.read()
        link = HTML.fromstring(page).xpath("//a/@href")[0]
#        decodes = urldecode(link)
#        link = decodes['u']
        if not link.startswith('http://'): link = 'http://weibo.cn/%s' % link
        req = urllib2.Request(link, headers=self.headers)
        # urllib2.urlopen(req)
        _urlopen(req)
        link = urldecode(link)
        self.fetch_params = urldecode(link['u'])
        if self.create:
            self.cj.save(filename=cookie_file)
        elif self.cj.filename is not None:
            self.cj.save()
        logger.info('login succeed!')

    def fetch(self, url):
        logger.info('fetch url:  %s', url)

        if not hasattr(self, 'fetch_params'):
            self.login()
        params = urldecode(url)
        params.update(self.fetch_params)
        url = '%s?%s' % (url.split('?', 1)[0], urllib.urlencode(params))

        req = urllib2.Request(url, headers=self.headers)
        return urllib2.urlopen(req).read()
