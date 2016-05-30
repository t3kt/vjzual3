print('shell/module.py initializing')

try:
	import common_base as base
except ImportError:
	import base
try:
	import common_util as util
except ImportError:
	import util

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

class Module(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def Shell(self):
		return self.comp.op('./shell')

	@property
	def BodyPanel(self):
		return self.comp.op('./body_panel')

	def UpdateHeight(self):
		pass

	@property
	def BodyHeight(self):
		raise NotImplementedError()

	def _UpdateBodyPanelHeight(self):
		panel = self.BodyPanel
		if not panel:
			return
		panel.par.h = util.GetVisibleChildCOMPsHeight(panel)
