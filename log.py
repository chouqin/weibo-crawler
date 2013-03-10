#!/usr/bin/env python
#coding=utf-8

import logging
import os

logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawler.log'), level=logging.DEBUG)
logger = logging.getLogger('liqi')
