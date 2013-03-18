#!/usr/bin/env python
#coding=utf-8

from pyquery import PyQuery as pq
from log import logger
from datetime import datetime, timedelta
import time
from fetcher import urldecode

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

class CnWeiboParser(object):
    def __init__(self, html, user, storage):
        self.user = user
        self.storage = storage
        self.doc = pq(html)

    def _strptime(self, string, format_):
        return datetime.strptime(string, format_)

    def parse_datetime(self, dt_str):
        dt = None
        if u'秒' in dt_str:
            sec = int(dt_str.split(u'秒', 1)[0].strip())
            dt = datetime.now() - timedelta(seconds=sec)
        elif u'分钟' in dt_str:
            sec = int(dt_str.split(u'分钟', 1)[0].strip()) * 60
            dt = datetime.now() - timedelta(seconds=sec)
        elif u'今天' in dt_str:
            dt_str = dt_str.replace(u'今天', datetime.now().strftime('%Y-%m-%d'))
            # dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            dt = self._strptime(dt_str, '%Y-%m-%d %H:%M')
        elif u'月' in dt_str and u'日' in dt_str:
            this_year = datetime.now().year
            # dt = datetime.strptime('%s %s' % (this_year, dt_str), '%Y %m月%d日 %H:%M')
            dt = self._strptime('%s %s' % (this_year, dt_str), '%Y %m月%d日 %H:%M')
        else:
            # dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            dt = self._strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return time.mktime(dt.timetuple())

    def parse(self):
        def _parse_weibo(i):
            node = pq(this)

            if node.attr('id') is None:
                return

            n = 0
            divs = node.children('div')
            for div in divs:
                if len(pq(div).find('img.ib')) == 0:
                    n += 1
            if n == 0:
                return

            weibo = {}
            is_forward = True if len(divs) == 2 else False
            content = pq(divs[0]).children('span.ctt').text()
            if is_forward:
                weibo['forward'] = content
            else:
                weibo['content'] = content
            if is_forward:
                div = pq(divs[-1])
                weibo['content'] = div.text().split(u'赞')[0].strip(u'转发理由:').strip()
            # get weibo's datetime
            dt_str = pq(divs[-1]).children('span.ct').text()
            if dt_str is not None:
                dt_str = dt_str.replace('&nbsp;', ' ').split(u'来自', 1)[0].strip()
            weibo['ts'] = int(self.parse_datetime(dt_str))
            self.storage.save_weibo(weibo)

        self.doc.find('div.c').each(_parse_weibo)

        pg = self.doc.find('div#pagelist.pa')
        if len(pg) == 1 and u'下页' in pg.text():
            url = pq(pg.find('a')[0]).attr('href')
            decodes = urldecode(url)
            if int(decodes['page']) > 20:
                return None
            return 'http://weibo.cn%s' % pq(pg.find('a')[0]).attr('href')
