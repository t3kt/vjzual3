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
			self._paramSpecsDat.clear()
			self._paramSpecsDat.appendRow(_allParSpecFields)
			m = self.TargetModule
			if not m:
				self._LogEvent('Rebuild() - no target module')
				return
			modspec = m.GetSchema()
			oldctrls = m.findChildren(tags=['autoctrl'], maxDepth=1)
			for ctrl in oldctrls:
				ctrl.destroy()
			self._LoadSchema(modspec)
			self._BuildControls(m, modspec)
			# ...?
			pass
		finally:
			self._LogEnd('Rebuild()')

	def _LoadSchema(self, modspec):
		self._LogBegin('_ReloadSchema()')
		try:
			self._schemaJsonDat.text = modspec.ToJson(indent='  ')
			_FillParTable(self._paramSpecsDat, modspec.params)
		finally:
			self._LogEnd('_ReloadSchema()')

	def _BuildControls(self, m, modspec):
		self._LogBegin('_BuildControls()')
		try:
			styleHandlers = {}
			styleHandlers[('Float', 1)] = _SingleSliderBuilder(
				hostop=m,
				hostopexpr='ext.tmod',
				layoutparentexpr='ext.tmod',
				template=self.comp.op('./templates/single_slider'))
			styleHandlers[('Int', 1)] = styleHandlers[('Float', 1)]

			nodeX = -160
			nodeY = 0
			for paramspec in modspec.params:
				stylekey = (paramspec.style, paramspec.length or 1)
				handler = styleHandlers.get(stylekey)
				if handler is None:
					self._LogEvent(
						'_BuildControls() - unsupported style (name: %r): %r'
						% (paramspec.key, stylekey))
					continue
				ctrl = handler.Build(paramspec)
				ctrl.nodeX = nodeX
				ctrl.nodeY = nodeY
				nodeY -= 120
			# ...?
			pass
		finally:
			self._LogEnd('_BuildControls()')

	def _RemoveControls(self):
		pass

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
	def __init__(self, hostop, hostopexpr, template, layoutparentexpr):
		self.hostop = hostop
		self.hostopexpr = hostopexpr
		self.template = template
		self.layoutparentexpr = layoutparentexpr

	def _CreateControl(self, paramspec):
		ctrl = self.hostop.copy(self.template, name=paramspec.key + '_ctrl')
		ctrl.tags.add('autoctrl')
		ctrl.color = (0.5450000166893005, 0.5450000166893005, 0.5450000166893005)
		ctrl.par.w.expr = self.layoutparentexpr + '.par.w'
		return ctrl

	def _InitializeControl(self, paramspec, ctrl):
		pass

	def Build(self, paramspec):
		ctrl = self._CreateControl(paramspec)
		self._InitializeControl(paramspec, ctrl)
		return ctrl

class _SingleSliderBuilder(_Builder):
	def __init__(self, hostop, hostopexpr, layoutparentexpr, template):
		super().__init__(
			hostop=hostop,
			hostopexpr=hostopexpr,
			template=template,
			layoutparentexpr=layoutparentexpr)

	def _InitializeControl(self, paramspec, ctrl):
		ctrl.par.Label = paramspec.label
		ctrl.par.Integer = paramspec.ptype == schema.ParamType.int
		if paramspec.defaultval is not None:
			ctrl.par.Default1 = paramspec.defaultval
		if paramspec.minnorm is not None:
			ctrl.par.Rangelow1 = paramspec.minnorm
		if paramspec.maxnorm is not None:
			ctrl.par.Rangehigh1 = paramspec.maxnorm
		ctrl.par.Value1.expr = self.hostopexpr + '.par.' + paramspec.key
