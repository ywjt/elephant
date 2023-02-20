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
"""


import sys, os
sys.path.append("..")
import ConfigParser
import datetime, time
from time import sleep
import functools
import threading
import logging
import psutil
from multiprocessing import Process, Queue
from lib import __VERSION__


CONF_DIR = '/etc/elephant.d/'
LOGS_DIR = '/var/log/elephant/'
CACHE_DIR = '/var/cache/'
if not os.path.exists(LOGS_DIR):
	os.system('mkdir -p %s' %LOGS_DIR)
	os.chmod(LOGS_DIR, 775)


"""
#==================================
# 加载配置文件
#==================================
"""
class LConf(object):
	cf = ''
	filepath = CONF_DIR + "elephantd.conf"

	def __init__(self):
		try:
			f = open(self.filepath, 'r')
		except IOError as e:
			print("\"%s\" Config file not found." % (self.filepath))
			sys.exit(1)
		f.close()

		self.cf = ConfigParser.ConfigParser()
		self.cf.read(self.filepath)

	def getSectionValue(self, section, key):
		return self.getFormat(self.cf.get(section, key))
	def getSectionOptions(self, section):
		return self.cf.options(section)
	def getSectionItems(self, section):
		return self.cf.items(section)
	def getFormat(self, string):
		return string.strip("'").strip('"').replace(" ","")


"""
#==================================
# 初始化主类参数
#==================================
"""
class Core(object):
	avr = {}

	def __init__(self):
		LC = LConf()
		self.avr['log_level'] = LC.getSectionValue('system', 'log_level')
		self.avr['log_file'] = LC.getSectionValue('system', 'log_file')
		self.avr['interface'] = LC.getSectionValue('system','interface')
		self.avr['diskpart'] = LC.getSectionValue('system','diskpart')
		self.avr['stream_type'] = LC.getSectionValue('system','stream_type')
		self.avr['my_host'] = LC.getSectionValue('mysql','my_host')
		self.avr['my_port'] = LC.getSectionValue('mysql','my_port')
		self.avr['my_user'] = LC.getSectionValue('mysql','my_user')
		self.avr['my_pwd'] = LC.getSectionValue('mysql','my_pwd')
		self.avr['my_db'] = LC.getSectionValue('mysql','my_db')
		self.avr['api_host'] = LC.getSectionValue('api','api_host')
		self.avr['api_token'] = LC.getSectionValue('api','api_token')
		self.avr['cus_model'] = LC.getSectionValue('custom','cus_model')
		

	def status(self):
		proc_info={}
		try:
			f = open(LOGS_DIR+'elephantd.pid', 'r')
			pid = int(f.read())
			p = psutil.Process(pid)
			proc_info["name"]=p.name()        #进程名
			proc_info["exe"]=p.exe()         #进程的bin路径
			proc_info["cwd"]=p.cwd()         #进程的工作目录绝对路径
			proc_info["status"]=p.status()      #进程状态
			proc_info["create_time"]=p.create_time()  #进程创建时间
			proc_info["running_time"]='%d Seconds' % int((time.time()-proc_info["create_time"]))
			proc_info["uids"]=p.uids()          #进程uid信息
			proc_info["gids"]=p.gids()           #进程的gid信息
			proc_info["cpu_times"]=p.cpu_times()      #进程的cpu时间信息,包括user,system两个cpu信息
			proc_info["cpu_affinity"]=p.cpu_affinity()   #get进程cpu亲和度,如果要设置cpu亲和度,将cpu号作为参考就好
			proc_info["memory_percent"]=p.memory_percent() #进程内存利用率
			proc_info["memory_info"]=p.memory_info()    #进程内存rss,vms信息
			proc_info["io_counters"]=p.io_counters()    #进程的IO信息,包括读写IO数字及参数
			proc_info["connections"]=p.connections()    #返回socket连接列表
			proc_info["num_threads"]=p.num_threads()  #进程开启的线程数

			active = "stoping" if proc_info["status"]=="stoping" else "running"
			print('Elephant v%s' % __VERSION__)
			print('Active: \033[32m active (%s) \033[0m, PID: %d (elephantd), Since %s' % (active, pid, time.strftime("%a %b %d %H:%M:%S CST", time.localtime())))
			proc_info=sorted(proc_info.iteritems(), key=lambda d:d[0], reverse=False) 
			for k, v in proc_info:
				if k=="connections":
					print('%s : ' % k)
					for l in v:
						print('     --| %s' % str(l))
				else:
					print('%s : %s ' % (k, str(v)))

		except IOError as e:
			print("elephantd not already running!")
			Loger().ERROR("elephantd not already running!")
			sys.exit(1)
		f.close()


"""
#==================================
#日志记录方法
#==================================
"""
class Loger(Core):
	def __init__(self):
		Core.__init__(self)

		if self.avr['log_file'].find("/") == -1:
			self.log_file = LOGS_DIR + self.avr['log_file']
		else:
			self.log_file = self.avr['log_file']

		if self.avr['log_level'].upper()=="DEBUG":
			logging_level = logging.DEBUG
		elif self.avr['log_level'].upper()=="INFO":
			logging_level = logging.INFO
		elif self.avr['log_level'].upper()=="WARNING":
			logging_level = logging.WARNING
		elif self.avr['log_level'].upper()=="ERROR":
			logging_level = logging.ERROR
		elif self.avr['log_level'].upper()=="CRITICAL":
			logging_level = logging.CRITICAL
		else:
			logging_level = logging.WARNING

		logging.basicConfig(level=logging_level, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=self.log_file,
                    filemode='a')

	def STDOUT(self):
		logger = logging.getLogger()
		ch = logging.StreamHandler()
		logger.addHandler(ch)
	def DEBUG(self, data):
		return logging.debug(data)
	def INFO(self, data):
		return logging.info(data)
	def WARNING(self, data):
		return logging.warning(data)
	def ERROR(self, data):
		return logging.error(data)
	def CRITICAL(self, data):
		return logging.critical(data)





