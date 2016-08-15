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
	COMP = object()

class ShellApp(base.Extension):
	def __init__(self, comp):
		self.comp = comp

	def Setup(self):
		page = self.comp.appendCustomPage('App')
		util.setattrs(page.appendCHOP('Ctrlinvals', label='Control In Vals'), default='./ctrlin_vals')

	@property
	def AllModules(self):
		return self.comp.findChildren(type=COMP, tags=['tmod'])

	@property
	def _GlobalChain(self):
		g = getattr(op, 'Global')
		if not g:
			raise Exception('Global chain not found!')
		return g

	@property
	def OutputSource(self):
		return self._GlobalChain.par.Source
