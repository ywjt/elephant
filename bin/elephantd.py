#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
* @ Elephant for Python
##############################################################################
# Author: YWJT / ZhiQiang Koo                                                #
# Modify: 2019-12-30                                                         #
##############################################################################
"""

import sys
sys.path.append("..")
import os, time, datetime
import atexit
import shutil
import platform
import fire
from signal import SIGTERM
from lib.base import Core, Loger
from lib.base import CONF_DIR, LOGS_DIR, CACHE_DIR
from lib.cores import Elephant
from lib import __VERSION__
PROC_DIR =  os.path.abspath('.')


class Daemon:
	"""
	daemon class.	
	Usage: subclass the Daemon class and override the _run() method
	"""
	def __init__(self, pidfile='/tmp/daemon.pid', stdin='/dev/null', stdout='/dev/null', stderr='/dev/stderr'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = LOGS_DIR + pidfile
	
	def _daemonize(self):
		#脱离父进程
		try: 
			pid = os.fork() 
			if pid > 0:
				sys.exit(0) 
		except OSError as e: 
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			Loger().ERROR("elephantd fork #1 failed:"+str(e.strerror))
			sys.exit(1)
		os.setsid() 
		os.chdir(PROC_DIR) 
		os.umask(0)
	
		#第二次fork，禁止进程重新打开控制终端
		try: 
			pid = os.fork() 
			if pid > 0:
				sys.exit(0) 
		except OSError as e: 
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			Loger().ERROR("elephantd fork #2 failed:"+str(e.strerror))
			sys.exit(1) 

		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0) 
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)
	
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError as e:
			pid = None
	
		if pid:
			message = "Start error,pidfile %s already exist. elephantd already running?\n"
			Loger().ERROR(message)
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)

		self._daemonize()
		self._run()

	def stop(self):
		"""
		Stop the daemon
		"""
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError as e:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. elephantd not running?\n"
			Loger().ERROR(message)
			sys.stderr.write(message % self.pidfile)
			return

		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError as err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
					Loger().WARNING("stop elephantd Success.")
			else:
				Loger().ERROR("stop error,"+str(err))
				sys.exit(1)

	def restart(self):
		self.stop()
		self.start()


class Console(Daemon):
	def _run(self):
		Loger().INFO('Elephant %s ' % __VERSION__)
		Loger().INFO('Copyright (C) 2011-2020, YWJT.org.')
		Loger().INFO('elephantd started with pid %d' % os.getpid())
		Loger().INFO('elephantd started with %s' % datetime.datetime.now().strftime("%m/%d/%Y %H:%M"))
		C=Elephant()
		try:
			fire.Fire(C.set)
			C.poll()
		except Exception as e:
				Loger().ERROR(str(e))
				raise
		#Elephant().poll()


class Tailf(Core):
	def __init__(self):
		Core.__init__(self)
		__logfilename = LOGS_DIR + self.avr['log_file']
		self.check_file_validity(__logfilename)
		self.tailed_file = __logfilename
		self.callback = sys.stdout.write
 
	def follow(self, s=1):
		print("logging output ......")
		with open(self.tailed_file) as file_:
			file_.seek(0, 2)
			while True:
				curr_position = file_.tell()
				line = file_.readline()
				if not line:
					file_.seek(curr_position)
				else:
					self.callback(line)
				time.sleep(s)
 
	def register_callback(self, func):
		self.callback = func
 
	def check_file_validity(self, file_):
		if not os.access(file_, os.F_OK):
			raise TailError("File '%s' does not exist" % (file_))
		if not os.access(file_, os.R_OK):
			raise TailError("File '%s' not readable" % (file_))
		if os.path.isdir(file_):
			raise TailError("File '%s' is a directory" % (file_))
 
class TailError(Exception):
	def __init__(self, msg):
		self.message = msg
	def __str__(self):
		return self.message


def help():
	__MAN = 'Usage: %s \n \
		          \n \
Options:  \n \
	daemon       start service for daemon. \n \
	start        start service for console. \n \
	[daemon|start] Args:                  \n \
		--iface=  point to network interface. (default: eth0) \n \
		--disk=   point to disk partition. (default: vdb)   \n \
		--lport=  point to monitoring ports. (default: 0)  \n \
		or --proc=   point to monitoring process name. (default: '')  \n \
		or --lpid=   point to monitoring process id. (default: 0)  \n \
		--istep=  second intervals of data acquisition. (default: 5)\n \
		--delay=  minute intervals of auto close. (default: 10)\n \
		--jid=    job id for record. (default: 0)\n \
	  Exps:  \n \
		elephantd daemon --iface=eth0 --disk=vdb --lport="6666,6667" --proc="procA,procB" --istep=5 --delay=10   \n \
	stop         stop daemon service. \n \
	status       show service run infomation. \n \
	watch        same as tailf, watching log output. \n \
	help         show this usage information. \n \
	version      show version information. \n \
	'
	print(__MAN % sys.argv[0])


if __name__ == '__main__':
	daemon = Console(pidfile='elephantd.pid')

	if len(sys.argv) > 1:
		if 'DAEMON' == (sys.argv[1]).upper():
			daemon.start()
		elif 'STOP' == (sys.argv[1]).upper():
			daemon.stop()
		elif 'HELP' == (sys.argv[1]).upper():
			help()
		elif 'VERSION' == (sys.argv[1]).upper():
			print('Elephant %s' % __VERSION__)
		elif 'WATCH' == (sys.argv[1]).upper():
			Tailf().follow()
		elif 'STATUS' == (sys.argv[1]).upper():
			Core().status()
		elif 'START' == (sys.argv[1]).upper():
			C=Elephant()
			try:
				fire.Fire(C.set)
				C.poll()
			except Exception as e:
					Loger().ERROR(str(e))
					raise

		else:
			print("Unknow Command!")
			help()
			sys.exit(1)
	else:
		Elephant().poll()
