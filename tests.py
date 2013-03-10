'''
Created on 2013-1-25

@author: Chine
'''
import unittest

from WeiboCrawler.fetcher import CnFetcher
from WeiboCrawler.parser import CnWeiboParser
from WeiboCrawler.storage import Storage
from WeiboCrawler.settings import account, pwd

class DebugStorage(Storage):
    def save_weibo(self, weibo):
        print weibo
    
    def save_weibos(self, weibos):
        for weibo in weibos:
            self.save_weibo(weibo)
    
    def save_info(self, info):
        print info
    
    def save_user(self, user):
        print user
    
    def save_users(self, users):
        for user in users:
            self.save_user(user)
    
    def complete(self):
        print 'complete %s' % self.uid
    
    def error(self):
        print 'error: %s' % self.uid
        
TEST_UID = '1644492510'
TEST_UID_URL = 'http://weibo.cn/jsbcmf'
TEST_UID_INFO_URL = 'http://weibo.cn/%s/info' % TEST_UID
TEST_UID_FOLLOW_URL = 'http://weibo.cn/%s/follow' % TEST_UID
TEST_UID_FANS_URL = 'http://weibo.cn/%s/fans' % TEST_UID

class Test(unittest.TestCase):
    
    def setUp(self):
        self.fetcher = CnFetcher(account, pwd)
        self.fetcher.login()
        self.storage = DebugStorage(TEST_UID)

    def testUid(self):
        html = self.fetcher.fetch(TEST_UID_URL)
        parser = CnWeiboParser(html, TEST_UID, self.storage)
        assert parser.get_uid() == TEST_UID

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()