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
		self._builders = _CreateBuilderSet(comp.op('./templates'))

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
			nodeX = -160
			nodeY = 0
			count = float(len(modspec.params))
			layoutparent = m.op('./controls_panel')
			for i, paramspec in enumerate(modspec.params):
				stylekey = (paramspec.style, paramspec.length or 1)
				handler = self._builders.get(stylekey)
				if handler is None:
					self._LogEvent(
						'_BuildControls() - unsupported style (name: %r): %r'
						% (paramspec.key, stylekey))
					continue
				ctrl = handler.Build(paramspec, m)
				ctrl.tags.add('autoctrl')
				ctrl.color = (0.5450000166893005, 0.5450000166893005, 0.5450000166893005)
				ctrl.nodeX = nodeX
				ctrl.nodeY = nodeY
				ctrl.par.w.expr = 'ext.tmod.par.w'
				ctrl.par.order = i / count
				if layoutparent is not None:
					ctrl.inputCOMPConnectors[0].connect(layoutparent)
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

def _CreateBuilderSet(templates):
	singleslider = templates.op('./single_slider')
	singlebutton = templates.op('./single_button')
	twosliders = templates.op('./two_sliders')
	threesliders = templates.op('./three_sliders')
	foursliders = templates.op('./four_sliders')
	builders = {}
	builders[('Toggle', 1)] = _SingleButtonBuilder(singlebutton, behavior='toggledown')
	builders[('Pulse', 1)] = _SingleButtonBuilder(singlebutton, behavior='pulse')
	builders[('Float', 1)] = _SingleSliderBuilder(singleslider)
	builders[('Int', 1)] = builders[('Float', 1)]
	multisliders = [
		None,
		twosliders,
		threesliders,
		foursliders,
	]
	for i in (2, 3, 4):
		suffixes = (1, 2, 3, 4)[:i]
		builders[('Float', i)] = _MultiSliderBuilder(
			multisliders[i - 1],
			suffixes=suffixes,
			labels=suffixes)
		builders[('Int', i)] = builders[('Float', i)]
	for style in ['RGB', 'RGBA', 'UV', 'UVW', 'XY', 'XYZ']:
		i = len(style)
		builders[(style, i)] = _MultiSliderBuilder(multisliders[i - 1], style[:i].lower(), style[:i])

	return builders

class _Builder:
	def __init__(self, template):
		self.template = template

	def Build(self, paramspec, hostop):
		ctrl = hostop.copy(self.template, name=paramspec.key + '_ctrl')
		return ctrl

class _SingleSliderBuilder(_Builder):
	def __init__(self, template):
		super().__init__(
			template=template)

	def Build(self, paramspec, hostop):
		ctrl = super().Build(paramspec, hostop)
		ctrl.par.Label = paramspec.label
		ctrl.par.Integer = paramspec.ptype == schema.ParamType.int
		if paramspec.defaultval is not None:
			ctrl.par.Default1 = paramspec.defaultval
		if paramspec.minnorm is not None:
			ctrl.par.Rangelow1 = paramspec.minnorm
		if paramspec.maxnorm is not None:
			ctrl.par.Rangehigh1 = paramspec.maxnorm
		ctrl.par.Value1.expr = 'ext.tmod.par.' + paramspec.key
		return ctrl

class _SingleButtonBuilder(_Builder):
	def __init__(self, template, behavior):
		super().__init__(template=template)
		self.behavior = behavior

	def Build(self, paramspec, hostop):
		ctrl = super().Build(paramspec, hostop)
		label = paramspec.label
		ctrl.par.Label = label
		ctrl.par.Texton = label
		ctrl.par.Textoff = label
		ctrl.par.Textonroll = label + ' on'
		ctrl.par.Textoffroll = label + ' off'
		if paramspec.defaultval is not None:
			ctrl.par.Default1 = paramspec.defaultval
		ctrl.par.Value1.expr = 'ext.tmod.par.' + paramspec.key
		ctrl.par.Behavior = self.behavior
		return ctrl

class _MultiSliderBuilder(_Builder):
	def __init__(self, template, suffixes, labels):
		super().__init__(template=template)
		self.count = len(suffixes)
		self.suffixes = suffixes
		self.labels = labels

	def Build(self, paramspec, hostop):
		ctrl = super().Build(paramspec, hostop)
		isint = paramspec.ptype == schema.ParamType.int
		for i in range(self.count):
			subctrl = ctrl.op('./par%d_slider' % (i + 1))
			subctrl.par.Label = self.labels[i]
			subctrl.par.Help = paramspec.label + ' ' + self.labels[i]
			subctrl.par.Integer = isint
			if paramspec.defaultval and paramspec.defaultval[i] is not None:
				subctrl.par.Default1 = paramspec.defaultval[i]
			if paramspec.minnorm and paramspec.minnorm[i] is not None:
				subctrl.par.Rangelow1 = paramspec.minnorm[i]
			if paramspec.maxnorm and paramspec.maxnorm[i] is not None:
				subctrl.par.Rangehigh1 = paramspec.maxnorm[i]
			subctrl.par.Value1.expr = 'ext.tmod.par.' + paramspec.key + self.suffixes[i]
		return ctrl
