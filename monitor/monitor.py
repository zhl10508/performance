# coding:utf-8
import time
import threading
import logging
import os

import util
import common
from api_manager import ApiManager
from ios_monitor import Monitor as iOSMonitor
from android_monitor import Monitor as androidMonitor

class Monitor(threading.Thread):
	def __init__(self, config):
		threading.Thread.__init__(self)
		self._intersec = 1
		self._thread_stop = False
		self._monitor = None
		new_gm_uid = config.generate_new_gm_uid()
		self._device_model = config.device_model
		self._api_mgr = ApiManager(new_gm_uid, config.attached_client_uid)
		self.setup_descriptors()
		if self._platform ==  common.PLATFORM_IOS:
			self._monitor = iOSMonitor(self._device_descriptor,
				self._app_descriptor)
		elif self._platform == common.PLATFORM_ANDROID:
			self._monitor = androidMonitor(self._device_descriptor,
				self._app_descriptor)
		self.setup_log()

	def setup_descriptors(self):
		self._platform = common.descriptors[self._device_model]['platform']
		self._device_descriptor = \
			common.descriptors[self._device_model]['device_descriptor'] or ''
		self._app_descriptor = \
			common.descriptors[self._device_model]['app_descriptor'] or ''

	def setup_log(self):
		log_file = 'profile-{model}.log'.format(model=self._device_model)
		log_path = os.path.join(util.LOG_PATH, log_file)
		file_handler = logging.FileHandler(log_path)
		formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s',
			datefmt='%H:%M:%S')
		file_handler.setFormatter(formatter)
		self._log = logging.getLogger('monitor_' + self._device_model)
		self._log.addHandler(file_handler)

	def run(self):
		while not self._thread_stop:
			if not self._monitor:
				self._log.info(
					'Here should be some data, but you dont have a monitor..')
			else:
				render_fps = self._api_mgr.to_exec(
					'profiling.get_render_rate()')
				memory = self._monitor.memory()
				VSS = memory['VSS']
				RSS = memory['RSS']
				self._log.info('cpu usage:{cpu}, VSS:{VSS},' \
					'RSS:{RSS}, fps:{render_fps}'.format(
					cpu=self._monitor.cpu(), VSS=VSS, RSS=RSS,
					render_fps=render_fps))
			time.sleep(self._intersec)

	def stop(self):
		self._thread_stop = True
		time.sleep(1)
		self._api_mgr.disconnect()