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
import requests
import json
from peewee import *
from lib.base import Core, Loger


try:
	settings = {'host': Core().avr['my_host'] , 'password': Core().avr['my_pwd'], 'port': int(Core().avr['my_port']), 'user':Core().avr['my_user']}
	mysql_db = MySQLDatabase(Core().avr['my_db'], **settings)
	mysql_db.connect()
except Exception as e:
	Loger().ERROR(str(e))
	raise
		

class Tbl_elephant(Model):
	jid = CharField(verbose_name='任务ID', index=True, default=0)
	cpu_idle = FloatField(verbose_name='CPU空闲', default=0.0)
	ioutil =   FloatField(verbose_name='磁盘IO', default=0.0)
	mem_free = BigIntegerField(verbose_name='空闲内存', default=0)
	netpack =  BlobField(verbose_name='网络发包率')
	netflow =  BlobField(verbose_name='网络流量')
	loadavg =  FloatField(verbose_name='机器负载', default=0.0)
	p_cpuuse = BlobField(verbose_name='进程占用CPU')
	p_io =   BlobField(verbose_name='进程占用IO')
	p_memuse = BlobField(verbose_name='进程占用内存')
	p_netpack =  BlobField(verbose_name='进程发包率')
	p_netflow =  BlobField(verbose_name='进程网络流量')
	p_conns =  BlobField(verbose_name='进程连接数')
	uptime = TimestampField(verbose_name='录入时间')

	class Meta:
		database = mysql_db


mysql_db.create_tables([Tbl_elephant])


class MYStream(object):
	# save object result
	def set(self, **kv):
		cursor = Tbl_elephant(
			                 jid = str(kv['jid']),
						cpu_idle = float(kv['cpu_idle']),
						ioutil =   float((kv['ioutil'])),
						mem_free = int(kv['mem_free']),
						netpack =  str(kv['netpack']),
						netflow =  str(kv['netflow']),
						loadavg =  float(kv['loadavg']),
						p_cpuuse = str(kv['p_cpuuse']),
						p_io =     str(kv['p_io']),
						p_memuse = str(kv['p_memuse']),
						p_netpack =str(kv['p_netpack']), 
						p_netflow =str(kv['p_netflow']),  
						p_conns =  str(kv['p_conns'])
					)
		return cursor.save()

	# test
	def get(self, event_id):
		if event_id:
			for item in Tbl_elephant.select().where(Tbl_elephant.event_id==event_id):
				print(item.netpack)
		else:
			for item in Tbl_elephant.select():
				print(item.netpack)






















