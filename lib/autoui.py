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

import json

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
			_FillParTable(parsdat, modspec.params)
		finally:
			self._LogEnd('Rebuild()')

_simpleParSpecFields = [
	'key',
	'label',
	'style',
	'length',
	'group',
]

_allParSpecFields = _simpleParSpecFields + [
	'default1', 'default2', 'default3', 'default4',
	'minnorm1', 'minnorm2', 'minnorm3', 'minnorm4',
	'maxnorm1', 'maxnorm2', 'maxnorm3', 'maxnorm4',
	'minlimit1', 'minlimit2', 'minlimit3', 'minlimit4',
	'maxlimit1', 'maxlimit2', 'maxlimit3', 'maxlimit4',
	'options',
	'tags',
]

def _Listify(val):
	if val is None:
		return ['', '', '', '']
	if not isinstance(val, list):
		val = [val]
	for i in range(len(val)):
		if val[i] is None:
			val[i] = ''
	return val + ([''] * (4 - len(val)))

def _FillParTable(parsdat, parspecs):
	parsdat.clear()
	parsdat.appendRow(_allParSpecFields)
	for parspec in parspecs:
		if False:
			parspec = schema.ParamSpec(None)
		i = parsdat.numRows
		parsdat.appendRow([])
		for attrname in _simpleParSpecFields:
			val = getattr(parspec, attrname)
			if val is not None:
				parsdat[i, attrname] = val
		_AddListFields(parsdat, i, 'default', parspec, 'defaultval')
		_AddListFields(parsdat, i, 'minnorm', parspec, 'minnorm')
		_AddListFields(parsdat, i, 'maxnorm', parspec, 'maxnorm')
		_AddListFields(parsdat, i, 'minlimit', parspec, 'minlimit')
		_AddListFields(parsdat, i, 'maxlimit', parspec, 'maxlimit')
		_AddJsonListField(parsdat, i, 'options', [o.JsonDict for o in parspec.options] if parspec.options else None)
		_AddJsonListField(parsdat, i, 'tags', parspec.tags)

def _AddListFields(parsdat, i, outprefix, parspec, srcname):
	vals = _Listify(getattr(parspec, srcname))
	parsdat[i, outprefix + '1'] = vals[0]
	parsdat[i, outprefix + '2'] = vals[1]
	parsdat[i, outprefix + '3'] = vals[2]
	parsdat[i, outprefix + '4'] = vals[3]

def _AddJsonListField(parsdat, i, outname, vals):
	if vals is not None:
		parsdat[i, outname] = json.dumps(vals)

class _Builder:
	def _Build(self, paramspec, hostop, layoutparentpath):
		raise NotImplementedError()

	def Build(self, paramspec, hostop, layoutparentpath='controls_panel'):
		return self._Build(paramspec, hostop, layoutparentpath)

class _SingleSliderBuilder(_Builder):
	def __init__(self, template):
		self._template = template

	def _Build(self, paramspec, hostop, layoutparentpath='controls_panel'):
		pass
