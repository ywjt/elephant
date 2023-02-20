#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
* @ Elephant for Python
##############################################################################
# Author: YWJT / ZhiQiang Koo                                                #
# Modify: 2019-11-06                                                         #
##############################################################################
# This program is distributed under the "Artistic License" Agreement         #
# The LICENSE file is located in the same directory as this program. Please  #
# read the LICENSE file before you make copies or distribute this program    #
##############################################################################

{
'cpu_idle': 86.9, 
'ioutil': 0.0, 
'mem_free': 2238492672, 
'netpack': {'recv': 3, 'send': 2}, 
'netflow': {'recv': 294, 'send': 324}, 
'loadavg': '0.05',
'p_netpack': [{1903: {'recv': 3, 'send': 2}}], 
'p_io': [{1903: {'read': 0, 'write': 0}}], 
'p_memuse': [{1903: 113569792}], 
'p_cpuuse': [{1903: 0.0}], 
'p_netflow': [{1903: {'recv': 294, 'send': 324}}], 
'p_conns': [{1903: 16}], 
'time': 1578295486
}
"""

import sys, os
sys.path.append("..")
import datetime, time
import pickle
import requests
import json
from peewee import *
from lib.base import Core


class APIStream(Core):

	def __init__(self):
		Core.__init__(self)
		self.api_host = self.avr['api_host']
		self.api_token = self.avr['api_token']

	def set(self, **kv):
		aheaders = {'Content-Type': 'application/json'}
		if self.api_host.find("http") == -1:
			url = "http://%s?token=%s" % (self.api_host, self.api_token)
		else:
			url = "%s?token=%s" % (self.api_host, self.api_token)
		response = requests.post(url, headers=aheaders, data = json.dumps(kv))
		return response.text





















