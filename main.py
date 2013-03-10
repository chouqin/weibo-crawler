#!/usr/bin/env python
#coding=utf-8


from urllib2 import URLError
import time

from log import logger
from crawler import UserCrawler
from fetcher import CnFetcher

def local(uids=[]):

    fetcher = CnFetcher()
    fetcher.login()

    connection_error = False

    while len(uids) > 0 or connection_error:
        if not connection_error:
            uid = uids.pop()
        try:
            crawler = UserCrawler(uid, fetcher)
            crawler.run()
            connection_error = False
        except URLError, e:
            logger.exception(e)
            connection_error = True
            time.sleep(10)

if __name__ == "__main__":
    import argparse
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    parser = argparse.ArgumentParser('Task to crawl sina weibo.')
    parser.add_argument('uids', metavar="uids", type=str, nargs="*",
                        help="uids to crawl")
    args = parser.parse_args()

    uids = args.uids
    local(uids)
