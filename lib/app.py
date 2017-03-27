print('shell/app.py initializing')

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

class ShellApp(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.DataNodeBank = comp.par.Datanodebank.eval()

	@property
	def AllModules(self):
		return self.comp.findChildren(type=COMP, tags=['tmod'])

	@property
	def _ChildModules(self):
		return self.comp.findChildren(type=COMP, tags=['tmod'], depth=1)

	def GetChildModule(self, modname):
		mods = self.comp.findChildren(depth=1, tags=['tmod'], parName='Modname', parValue=modname)
		if not mods:
			return None
		return mods[0]

	@property
	def _GlobalChain(self):
		g = getattr(op, 'Global')
		if not g:
			raise Exception('Global chain not found!')
		return g

	@property
	def OutputSource(self):
		return self._GlobalChain.par.Source

	@property
	def _Key(self):
		return self.comp.par.Schemakey.eval() or project.name.replace('\.toe', '')

	@property
	def _Title(self):
		return self.comp.par.Title.eval() or self._Key

	def GetSchema(self):
		self._LogEvent('GetSchema()')
		key = self._Key
		childprefix = '/' + key
		return schema.AppSchema(
			key,
			label=self._Title,
			connections=[
				schema.ConnectionInfo(
					conntype='oscin',
					port=self.comp.par.Oscinport.eval(),
				),
				schema.ConnectionInfo(
					conntype='oscout',
					host=self.comp.par.Oscouthost.eval() or self.comp.par.Oscouthost.default,
					port=self.comp.par.Oscoutport.eval(),
				)
			],
			children=schema.BuildModuleSchemas(
				self._ChildModules,
				pathprefix=childprefix))

