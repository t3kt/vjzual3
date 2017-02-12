print('shell/autoui.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base
try:
	import common_util as util
except ImportError:
	try:
		import util
	except ImportError:
		import common.lib.util as util
try:
	import shell_mapping as mapping
except ImportError:
	import mapping
try:
	import shell_schema as schema
except ImportError:
	import schema

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

class AutoUI(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self._schemaJsonDat = comp.op('./set_schema_json')
		self._paramSpecsDat = comp.op('./set_param_specs')

	@property
	def TargetModule(self):
		if False:
			from module import Module
			return Module(None)
		return self.comp.par.Targetmodule.eval()

	def Rebuild(self):
		self._LogBegin('Rebuild()')
		try:
			self._schemaJsonDat.clear()
			m = self.TargetModule
			if not m:
				self._LogEvent('Rebuild() - no target module')
				return
			modspec = m.GetSchema()
			self._schemaJsonDat.text = modspec.ToJson(indent='  ')
			parsdat = self._paramSpecsDat
			parsdat.clear()
			#parsdat.appendRow(['key','label','type','style','group','default','minNorm','maxNorm',''])
			pass
		finally:
			self._LogEnd('Rebuild()')
