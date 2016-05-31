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

	@property
	def _HeaderHeight(self):
		return 20 if self.comp.par.Collapsed else 40

	@property
	def _BodyHeight(self):
		if self.comp.par.Collapsed:
			return 0
		panel = self.BodyPanel
		return panel.par.h if panel else 20

	def UpdateHeight(self):
		self._UpdateBodyPanelHeight()
		h = self._HeaderHeight
		h += self._BodyHeight
		self.comp.par.h = h

	def _UpdateBodyPanelHeight(self):
		panel = self.BodyPanel
		if not panel:
			return
		panel.par.h = util.GetVisibleChildCOMPsHeight(panel)
