#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-10-30

@author: Chine
'''

import urllib2
#import threading
import time
import random

from parser import (
    CnInfoParser,
    CnRelationshipParser,
    check_page_right,
)
from storage import FileStorage
from log import logger

def iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

#class UserCrawler(threading.Thread):
class UserCrawler():
    def __init__(self, user, fetcher):
        #super.__init__()

        logger.info('fetch user: %s' % user)
        self.url = 'http://weibo.cn/u/%s' % user
        self.fetcher = fetcher
        self.storage = FileStorage(user)
        self.user = user

        self.user_not_exist = False
        html = self._fetch(self.url)
        if html is None:
            self.user_not_exist = True
            self.error = True
            logger.info("html is none")
        elif not self._check_user_exist(html):
            self.error = True
            self.user_not_exist = True
            logger.info("user not exist")
        else:
            self.error = False

    def _check_user_exist(self, html):
        # If user not exist or forbiddened by weibo, directly return False
        if u'抱歉，您当前访问的用户状态异常，暂时无法访问。' in html:
            self.error = True
            self.user_not_exist = True
            return False
        return True

    def _fetch(self, url):
        html = self.fetcher.fetch(url)
        if not self._check_user_exist(html):
            return
        right = check_page_right(html)
        tries = 0
        while not right and tries <= 6:
            time.sleep(10)
            self.fetcher.login()
            sec = 10 * (tries + 1) if tries <= 2 else (
                600 * (tries - 2) if tries < 6 else 3600)
            time.sleep(sec)
            html = self.fetcher.fetch(url)
            if not self._check_user_exist(html):
                return
            right = check_page_right(html)
            if right:
                return html
            tries += 1
        else:
            return html
        self.error = True

    @property
    def info_link(self):
        return 'http://weibo.cn/%s/info' % self.user

    @property
    def follow_link(self):
        return 'http://weibo.cn/%s/follow' % self.user

    def _crawl(self, url, parser_cls):
        def start(url):
            html = self._fetch(url)
            parser = parser_cls(html, self.user, self.storage)
            return parser.parse()

        error = None
        for i in range(3):
            try:
                return start(url)
            except urllib2.HTTPError, e:
                if e.code == 404:
                    self.error = True
                    continue
                else:
                    error = e
                    continue
            except urllib2.URLError, e:
                error = e
                continue
            time.sleep(i * 5)
        if error is not None:
            raise error

    def _get_random_sec(self, maximun=40):
        return random.random() * maximun

    def crawl_info(self):
        url = self.info_link
        self._crawl(url, CnInfoParser)

    def crawl_follow(self):
        url = self.follow_link
        while url is not None:
            url = self._crawl(url, CnRelationshipParser)
            #if self.span:
                #time.sleep(self._get_random_sec())

    def crawl(self):
        if self.error is True:
            return

        logger.info("start to fetch %s's follow" % self.user)
        self.crawl_follow()
        logger.info("start to fetch %s's info" % self.user)
        self.crawl_info()

        # Add to completes when finished
        self.storage.complete()

    def run(self):
        assert self.storage is not None
        try:
            self.crawl()
        except Exception, e:
            logger.info('error when crawl: %s' % self.user)
            logger.exception(e)
        finally:
            if hasattr(self.storage, 'close'):
                self.storage.close()
