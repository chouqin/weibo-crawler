#coding=utf-8

import os
from settings import folder

class FileStorage():
    def __init__(self, user):
        self.path = os.path.join(folder, str(user))
        self.crawled = os.path.exists(self.path)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.info_f_path = os.path.join(self.path, 'info.txt')
        self.info_f = open(self.info_f_path, 'w')

        self.users_f_path = os.path.join(self.path, 'users.txt')
        self.users_f = open(self.users_f_path, 'w+')

        self.weibo_f_path = os.path.join(self.path, 'weibos.txt')
        self.weibo_f = open(self.weibo_f_path, 'w+')

        self.user = user

    def save_info(self, info):
        self.info_f.write("uid\t昵称\t性别\t地区\t生日\t简介\t标签\n")
        self.info_f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % tuple(info))
        #for k, v in info.iteritems():
            #self.info_f.write('%s：%s\n' % (k, v))

    def save_user(self, user_tuple):
        self.users_f.write('%s：%s' % user_tuple + '\n')

    def save_weibo(self, weibo):
        result = unicode(weibo['content'])
        if 'forward' in weibo:
            result += '// %s' % weibo['forward']
        self.weibo_f.write(result + ' ' + str(weibo['ts']) + '\n')

    def save_users(self, user_tuples):
        for user_tuple in user_tuples:
            self.save_user(user_tuple)

    def error(self):
        f = open(os.path.join(self.path, 'errors.txt'), 'w+')
        try:
            f.write(str(self.uid) + '\n')
        finally:
            f.close()

    def complete(self):
        f = open(os.path.join(self.path, 'completes.txt'), 'w+')
        try:
            f.write(str(self.user) + '\n')
        finally:
            f.close()

    def close(self):
        self.info_f.close()
        self.users_f.close()
        self.weibo_f.close()
