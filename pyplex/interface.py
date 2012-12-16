from commands.xbmc import xbmcCommands
from gui.image import image
import platform
from listeners.udplistener import udplistener
from listeners.httplistener import httplistener
from service.zeroconf import ZeroconfService
import Queue
from pprint import pprint
# from interfaces.plexInterface import plexInterface
# from interfaces.plexInterface
# from listners.httplistner import
class pyPlex():
	"""Wrapper class for pyPlex"""
	def __init__(self, arg):
		self.omxCommand = self.getArg(arg)
		self.hostname = platform.uname()[1]

	def start(self):
		"""Setting up listners and all other stuff"""
		# try:
		print "Setting up listeners, please wait..."
		global service
		global queue
		global parsed_path
		global media_key
		global duration
		self.service = ZeroconfService(name=self.hostname + " PyPlex", port=3000, text=["machineIdentifier=" + self.hostname,"version=2.0"])
		self.service.publish()
		self.duration = 0
		self.xbmcCmmd = xbmcCommands(self.omxCommand)
		self.media_key = None
		self.parsed_path = None
		self.queue = Queue.Queue()
		self.udp = udplistener(self.queue)
		self.udp.start()
		self.http = httplistener(self.queue)
		self.http.start()
		# __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		# f = open(os.path.join(__location__, 'image/logo.png'));
		# image = image(f)
		#image.set()
		# except:
		# 	print "error accoured"
		
	def run(self):
		"""Run pyPlex"""
		print "Starting pyPlex..."
		try:
			while True:
				command = self.parseCommand()
				if command:
					func, args = command
					func(*args)
					if(self.xbmcCmmd.shutDown):
						self.stop()
						return 0
					if(self.xbmcCmmd.isRunning()):
						self.xbmcCmmd.updatePosition()
		except Exception, e:
			print "Caught exception"
			message = 'There went something wrong in %s'
			if(self.xbmcCmmd):
				print message % 'xbmc'
				print e
				self.xbmcCmmd.Stop("")
				self.stop()
				return 0
			if(udp):
				print message % 'udp'
				print e
				self.udp.stop()
				self.udp.join()
			if(http):
				print message % 'http'
				print e
				self.http.stop()
				self.http.join()
			raise

	def getArg(self, arg):
		if len(arg) > 1: 
			if arg[1] == "hdmi":
				self.omxCommand = '-o hdmi'
				print "Audo output over HDMI"
		else:
			self.omxCommand = ''
			print "Audio output over 3,5mm jack"

	def parseCommand(self):
		try:
			command, args = self.queue.get(True, 2)
			print "Got command: %s, args: %s" %(command, args)
			if not hasattr(self.xbmcCmmd, command):
				print "Command %s not implemented yet" % command
			else:
				func = getattr(self.xbmcCmmd, command)
				return [func, args]
		except Queue.Empty:
			pass

	def stop(self):
		self.xbmcCmmd.Stop("")
		self.udp.stop()
		self.http.stop()
		self.service.unpublish()
