#!/usr/bin/python
# coding: utf-8

# Copyright (c) 2013 Mountainstorm
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from amdevice import *
from plistservice import *


class InstallationProxy(PlistService):
	def __init__(self, amdevice):
		PlistService.__init__(
			self, 
			amdevice, 
			[AMSVC_INSTALLATION_PROXY], 
			kCFPropertyListXMLFormat_v1_0
		)

	def lookup_applications(self):
		retval = []
		self._sendmsg({
			u'Command': u'Browse',
			u'ClientOptions': {
				u'ApplicationType': u'Any'
			}
		})
		while True:
			reply = self._recvmsg()
			if (    reply is None 
				or (    u'Status' in reply 
					and reply[u'Status'] == u'Complete')):
				break # done
			retval.append(reply[u'CurrentList'])
		return retval

	def install_application(self, path, options=None, progress=None):
		u'''Install an application from the /PublicStaging directory'''
		self._install_or_upgrade(True, path, options, progress)

	def upgrade_application(self, path, options=None, progress=None):
		u'''Upgrade an application from the /PublicStaging directory'''
		self._install_or_upgrade(False, path, options, progress)

	def _install_or_upgrade(self, install, path, options=None, progress=None):
		def callback(cfdict, arg):
			pass

		cfpath = CFTypeFrom(path)
		if options is not None:
			cfoptions = CFTypeFrom(options)
		else:
			cfoptions = CFTypeFrom({
				u'PackageType': u'Developer'
			})
		cb = AFCProgressCallback(callback)
		if progress is not None:
			cb = AFCProgressCallback(progress)
		if install:
			err = AMDeviceInstallApplication(self.s, cfpath, cfoptions, cb, None)
		else:
			err = AMDeviceUpgradeApplication(self.s, cfpath, cfoptions, cb, None)
		CFRelease(cfpath)
		CFRelease(cfoptions)
		if err != MDERR_OK:
			raise RuntimeError(u'Unable to install application', err)

	# TODO: archive, restore, etc


if __name__ == u'__main__':
	import pprint
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		ip = InstallationProxy(d)

		#pprint.pprint(ip.lookup_applications())
		AMDSetLogLevel(0xff)
		ip.install_application(u'MobileReplayer.app')
		AMDSetLogLevel(0x0)

		ip.disconnect()
		return d
	
	handle_devices(factory)

