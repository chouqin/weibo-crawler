#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-11-12

@author: Chine
'''

import logging
import os

logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawler.log'), level=logging.DEBUG)
logger = logging.getLogger('liqi')
