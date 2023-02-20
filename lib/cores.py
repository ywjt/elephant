#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
* @ Elephant for Python
##############################################################################
# Author: YWJT / ZhiQiang Koo                                                #
# Modify: 2019-12-30                                                         #
##############################################################################
采集数据：
【IO使用】    【CPU空闲】    【load负载】   【内存空闲】     【流出/流入】【发包率】
【进程CPU空闲】【进程内存空闲】【进程IO使用率】【进程流出/流入】【进程发包率】
"""



import sys, os
sys.path.append("..")
import re, time, datetime
import psutil
import functools
import threading
import commands
import fire
from time import sleep
from lib import __VERSION__
from lib.base import Core, Loger
from lib.base import CONF_DIR, LOGS_DIR, CACHE_DIR
__STREAM_TYPE = Core().avr['stream_type']
_CUSTOM_MODEL = Core().avr['cus_model']
if __STREAM_TYPE == 'mysql': from lib.mystream import *
if __STREAM_TYPE == 'api': from lib.apistream import *
if __STREAM_TYPE == 'custom': 
	__ROOT = os.path.dirname(os.path.abspath(sys.executable))
	sys.path.append(__ROOT.replace('bin','lib'))
	from custom import *


class Elephant(Core):

	timeout=1
	data={}
	pinfo=[]
	pname=[]

	'''
	@iface : 网络接口    string  default 'eth0'
	@disk  : 磁盘分区    string  default 'vdb'
	@istep : 步进时间(s) int     default 1
	@delay : 结束时间(m) int     default 10
	'''
	def __init__(self):
		Core.__init__(self)

	def set(self, iface, disk, proc='', lport=0, lpid=0, istep=None, delay=None, jid=0, x=None):
		self.interface=iface if iface else self.avr['interface']
		self.diskpart=disk   if disk  else self.avr['diskpart']
		self.delay=delay     if delay else 10
		self.istep=istep     if istep else 5
		self.jid = jid
		p_name=list(proc) if type(proc)==tuple else [proc]
		
		sys.stderr.write("Args Set: ")
		sys.stderr.write("(%s %s %s %s %s %s %s) \n" % (self.interface, self.diskpart, p_name, lport, lpid, self.istep, self.delay))
		self.check_io_env()
		self.p_get_ider(lpid, lport, p_name)
		self.p_get_name()


	def check_io_env(self):
		net_io_list =  psutil.net_io_counters(pernic=True).keys()
		disk_io_list = psutil.disk_io_counters(perdisk=True).keys()
		if self.interface in net_io_list and self.diskpart in disk_io_list:
			sys.stderr.write("Running: successd\n")
		else:
			sys.stderr.write("Running: error\n")
			sys.exit(1)



	'''
	#一个公共字典用于组合输出
	@key   : 字典名  string
	@value : 字典值  string/int/...
	'''
	def add(self, key, value):
		self.data[key] = value


	'''
	#网络数据采集
	#包含流量、包转发
	@return : 元组 tuple
	'''
	def net_io_counters(self):
		net_io = psutil.net_io_counters(pernic=True)
		net_recv = net_io[self.interface].bytes_recv
		net_send = net_io[self.interface].bytes_sent
		pck_recv = net_io[self.interface].packets_recv
		pck_send = net_io[self.interface].packets_sent
		return (float(net_recv), float(net_send), float(pck_recv), float(pck_send))

	'''
	#统计进程的网络信息
	#包含流量、包转发
	@pid : 进程号 int
	'''
	def p_net_line(self, pid):
		try:
			f = open('/proc/%s/net/dev' %pid, 'r')
			lines= f.readlines()[2:]
			f.close()
			for line in lines:
				line = line.strip()
				line = line.replace(' ','@').replace('@@@','').replace(':','')
				line = line.split('@')
				if line[0] == self.interface:
					break
		except Exception as e:
			raise
		return line

	'''
	#检索指定pid/端口/进程名
	#返回进程号、进程名称
	@pinfo : 字典 dict
	'''
	def p_get_ider(self, lpid, lport, p_name):
		Apinfo=[]
		Bpinfo=[]
		Cpinfo=[]
		Dpinfo=[]
		#检索进程号
		if not lpid in ['start','daemon'] and lpid!=0:
			if type(lpid)==tuple:
				Apinfo = [{'pid':int(pid)} for pid in lpid]
			else:
				Apinfo = [{'pid':int(lpid)}]

		#检索端口
		if not lport in ['start','daemon'] and lport!=0:
			ports=list(lport) if type(lport)==tuple else [lport]
			#转成字符串
			ports=[str(x) for x in ports]
			status, output = commands.getstatusoutput("netstat -ntlp|awk '/%s/ {print int($NF)}'" % ('|'.join(ports)))
			if output:
				Bpinfo = [{'pid':int(pid)} for pid in output.split('\n')]

		#检索进程名
		if p_name:
			Cpinfo = [{'pid':int(p.info['pid'])} for p in psutil.process_iter(attrs=['pid', 'name']) if p.info['name'] in p_name]

		Dpinfo.extend(Apinfo)
		Dpinfo.extend(Bpinfo)
		Dpinfo.extend(Cpinfo)
		self.pinfo = Dpinfo


	'''
	#查找pid对应的进程名字
	@pname : 列表 list
	'''
	def p_get_name(self):
		lname = {}
		try:
			if self.pinfo:
				for item in self.pinfo:
					f = open('/proc/%s/stat' % item['pid'], 'r')
					stat = f.read().split(" ")
					lname[item['pid']] = "%d_%s" % (item['pid'], stat[1].replace('(','').replace(')',''))
				self.pname=lname
		except IOError as e:
			Loger.ERROR(str(e))
			raise AutoExit(str(e))


	'''
	#cpu空闲率
	'''
	def cpu_idle(self, key):
		value = psutil.cpu_times_percent(1, False).idle
		return self.add(key, value)

	#磁盘IO
	def ioutil(self, key):
		disks_before = psutil.disk_io_counters(perdisk=True)
		time.sleep(1)
		disks_after = psutil.disk_io_counters(perdisk=True)
		read_sec = int(disks_after[self.diskpart].read_count - disks_before[self.diskpart].read_count)
		write_sec = int(disks_after[self.diskpart].write_count - disks_before[self.diskpart].write_count)
		busy_time_sec = (disks_after[self.diskpart].busy_time - disks_before[self.diskpart].busy_time)/10000.
		value = round((read_sec + write_sec) * busy_time_sec, 2)
		return self.add(key, value)

	'''
	#内存空闲
	'''
	def mem_free(self, key):
		mem = psutil.virtual_memory()
		value = mem.free
		return self.add(key, value)

	'''
	#网络流量
	'''
	def netflow(self, key):
		net = {}
		(recv, send,x,y) = self.net_io_counters()
		while True:  
			time.sleep(1)
			(new_recv, new_send,x,y) = self.net_io_counters() 
			net['recv'] = int(new_recv - recv)
			net['send'] = int(new_send - send)
			value = net
			return self.add(key, value)

	'''
	#网络发包
	'''
	def netpack(self, key):
		net = {}
		(x,y,recv, send) = self.net_io_counters()
		while True:  
			time.sleep(1)
			(x,y,new_recv, new_send) = self.net_io_counters() 
			net['recv'] = int(new_recv - recv)
			net['send'] = int(new_send - send)
			value = net
			return self.add(key, value)

	'''
	#load负载
	'''
	def loadavg(self, key):
		loadavg = {}
		f = open("/proc/loadavg","r")
		con = f.read().split()
		f.close()
		value = con[0]
		return self.add(key, value)

	'''
	#进程cpu
	'''
	def p_cpuuse(self, key):
		value=[]
		D={}
		if self.pinfo:
			for item in self.pinfo:

				p = psutil.Process(item['pid'])
				cpu = p.cpu_percent()
				D[self.pname[item['pid']]] = cpu
			value.append(D)
			return self.add(key, value)

	'''
	#进程内存
	'''
	def p_memuse(self, key):
		value=[]
		D={}
		if self.pinfo:
			for item in self.pinfo:
				p = psutil.Process(item['pid'])
				mem = p.memory_info().rss
				D[self.pname[item['pid']]] = mem
			value.append(D)
			return self.add(key, value)

	'''
	#进程IO
	'''
	def p_io(self, key):
		value=[]
		D={}
		if self.pinfo:
			for item in self.pinfo:
				p = psutil.Process(item['pid'])
				io_before = p.io_counters()
				time.sleep(1)
				io_after = p.io_counters()
				io_read = int(io_after.read_bytes - io_before.read_bytes)
				io_write = int(io_after.write_bytes - io_before.write_bytes)
				D[self.pname[item['pid']]] = {'read':io_read, 'write':io_write}
			value.append(D)
			return self.add(key, value)

	'''
	#进程发包率
	'''
	def p_netpack(self, key):
		value=[]
		D={}
		if self.pinfo:
			for item in self.pinfo:
				line_before = self.p_net_line(item['pid'])
				time.sleep(1)
				line_after = self.p_net_line(item['pid'])
				recv = int(line_after[2]) - int(line_before[2])
				if len(line_after) == 19:
					send = int(line_after[11]) - int(line_before[11])
				else:
					send = int(line_after[10]) - int(line_before[10])
				D[self.pname[item['pid']]] = {'recv':recv, 'send':send}
			value.append(D)
			return self.add(key, value)

	'''
	#进程流量
	'''
	def p_netflow(self, key):
		value=[]
		D={}
		if self.pinfo:
			for item in self.pinfo:
				line_before = self.p_net_line(item['pid'])
				time.sleep(1)
				line_after = self.p_net_line(item['pid'])
				recv = int(line_after[1]) - int(line_before[1])
				send = int(line_after[9]) - int(line_before[9])
				D[self.pname[item['pid']]] = {'recv':recv, 'send':send}
			value.append(D)
			return self.add(key, value)


	'''
	#进程连接数
	'''
	def p_conns(self, key):
		value=[]
		D={}
		if self.pinfo:
			for item in self.pinfo:
				p = psutil.Process(item['pid'])
				count=[conn for conn in p.connections("inet4") if conn.status=='ESTABLISHED']
				D[self.pname[item['pid']]] = len(count)
			value.append(D)
			return self.add(key, value)



	'''
	#保存到远程MySQL
	'''
	def to_remote_mysql(self, **kwargs):
		try:
			MYStream().set(**kwargs)
			Loger().INFO("send to mysql success.")
		except Exception as e:
			Loger().ERROR(str(e))
			pass


	'''
	#POST到远程接口
	'''
	def to_remote_api(self, **kwargs):
		try:
			res=APIStream().set(**kwargs)
			Loger().INFO("send to remote api success: %s" % res)
		except Exception as e:
			Loger().ERROR(str(e))
			pass


	'''
	#自定义执行接口
	'''
	def to_custom_api(self, **kwargs):
		try:
			cls_name = _CUSTOM_MODEL.split('.')[0]
			cls_func = _CUSTOM_MODEL.split('.')[1]
			exe_func = getattr(eval(cls_name)(), cls_func)
			res=exe_func(**kwargs)
			Loger().INFO("send to custom api success: %s" % res)
		except Exception as e:
			Loger().ERROR(str(e))
			pass


	'''
	#启动多线程
	@target_func : 传入函数名 list default []
	'''
	def run_thread(self, target_func=[]):
		nb = {}
		if target_func:
			for func in target_func:
				nb[func.__name__] = threading.Thread(target=func, args=(func.__name__,))
			for k in nb:
				nb[k].start()
			for k in nb:
				nb[k].join()



	'''
	#多线程并发循环
	'''
	def poll(self):
		etime=int(time.time()+self.delay*60+10)

		while True:
			if etime <= int(time.time()):
				Loger().WARNING("Time was over to %s minute, elephantd stop." % self.delay)
				raise AutoExit("Poll is auto exit.")
			else:
				self.run_thread([self.cpu_idle, self.mem_free, self.loadavg, 
									self.netflow, self.netpack, self.ioutil, 
									self.p_cpuuse, self.p_memuse, self.p_io, 
									self.p_netpack, self.p_netflow, self.p_conns])
				
				self.data['jid'] = self.jid
				self.data['uptime'] = int(time.time())
				print(self.data)
				if self.avr['stream_type'] == 'api':
					self.to_remote_api(**self.data)
				elif self.avr['stream_type'] == 'mysql':
					self.to_remote_mysql(**self.data)
				elif self.avr['stream_type'] == 'custom':
					self.to_custom_api(**self.data)
				else:
					Loger().WARNING("this stream_type not supported!")
				Loger().INFO(self.data)
				time.sleep(self.istep)


class AutoExit(Exception):
	def __init__(self, msg):
		self.message = msg
	def __str__(self):
		return self.message


