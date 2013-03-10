#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-10-23

@author: Chine
'''

# added for datetime.strptime is not thread-safe
#from threading import Lock

from pyquery import PyQuery as pq
from log import logger

def check_page_right(html):
    try:
        doc = pq(html)
        title = doc.find('title').text().strip()
        logger.info(title)
        return title != u'微博广场' and title != u'新浪微博-新浪通行证'
    except AttributeError:
        logger.info("attribute error")
        return False

class CnInfoParser(object):
    def __init__(self, html, user, storage):
        self.user = user
        self.storage = storage
        self.doc = pq(html)

    def parse(self):
        div = self.doc.find('div.tip:first').next('div.c').html()
        if div is None:
            return
        div = div.replace('\n', '').replace('<br />', '<br/>')
        info = {}
        for itm in div.split('<br/>'):
            if len(itm.strip()) == 0:
                continue
            kv = tuple(itm.split(':', 1))
            if len(kv) != 2 or len(kv[1].strip()) == 0:
                continue
            k, v = kv[0], pq(kv[1]).text().strip('更多>>').strip()
            info[k] = v

        keys = [
            u'昵称',
            u'性别',
            u'地区',
            u'生日',
            u'简介',
            u'标签',
        ]
        result = [self.user]
        for key in keys:
            if key in info:
                result.append(info[key])
            else:
                result.append("")

        self.storage.save_info(result)
        return info

class CnRelationshipParser(object):
    def __init__(self, html, user, storage):
        self.user = user
        self.storage = storage
        self.doc = pq(html)

    def parse(self):
        def _parse_user(i):
            node = pq(this)
            if len(node.children('img')) == 0:
                return
            src = node.children('img:first').attr('src')
            uid = src.split("/")[3]
            # self.storage.save_user((node.attr('href'), node.text(), ))
            self.storage.save_user((uid, self.user, ))

        self.doc.find('table tr td a:first').each(_parse_user)

        pg = self.doc.find('div#pagelist.pa')
        logger.info(pg.text())
        if len(pg) == 1 and u'下页' in pg.text():
            return 'http://weibo.cn%s' % pq(pg.find('a')[0]).attr('href')
