print('shell/app.py initializing')

try:
	import common_base as base
except ImportError:
	import base
try:
	import common_util as util
except ImportError:
	import util
try:
	import shell_mapping as mapping
except ImportError:
	import mapping

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

class ShellApp(base.Extension):
	def __init__(self, comp):
		self.comp = comp

	@property
	def GlobalChain(self):
		g = getattr(op, 'Global')
		if not g:
			raise Exception('Global chain not found!')
		return g

	@property
	def OutputSource(self):
		return self.GlobalChain.par.Source

	@OutputSource.setter
	def OutputSource(self, val):
		self.GlobalChain.par.Source = val

	def ResetOutputSource(self):
		p = self.OutputSource
		p.val = p.default

	def ToggleOutputSource(self, source):
		if source is None or self.OutputSource == source:
			self.ResetOutputSource()
		else:
			self.OutputSource = source
