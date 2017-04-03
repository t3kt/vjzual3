print('shell/schema.py initializing')

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

import sys
import os
import os.path
# _pytctrlpath = op('/_').var('shelldir')
_pytctrlpath = project.folder
_pytctrlpath = _pytctrlpath.replace('/', os.sep)
_pytctrlpath = os.path.join(_pytctrlpath, 'pytctrl')
if _pytctrlpath not in sys.path:
	sys.path.append(_pytctrlpath)

# export these so this module acts as a proxy
from tctrl.schema import ParamType, ParamOption, ParamPartSpec, ParamSpec, ModuleSpec, ConnectionInfo, AppSchema, GroupInfo, ModuleTypeSpec

class _ParStyleHandler:
	def SpecFromTuplet(self, tuplet): pass

class _SimpleHandler(_ParStyleHandler):
	def __init__(self, ptype, hasoptions=False, hasvalueindex=False):
		self.ptype = ptype
		self.hasoptions = hasoptions
		self.hasvalueindex = hasvalueindex

	def SpecFromTuplet(self, tuplet, pathprefix=None, getoptions=None, metadata=None, **kwargs):
		par = tuplet[0]
		options = getoptions(par.tupletName) if getoptions else None
		if options is None:
			options = _OptionsFromPar(par) if self.hasoptions else None
		if not metadata:
			metadata = {}
		return ParamSpec(
			par.tupletName,
			label=par.label,
			ptype=self.ptype,
			path=(pathprefix + par.tupletName) if pathprefix else None,
			style=par.style,
			group=par.page.name,
			defaultval=par.default,
			value=par.eval(),
			valueindex=par.menuIndex if self.hasvalueindex else None,
			options=options,
			help=metadata.get('help', None),
			tags=_GetTagsFromParMetadata(metadata),
		)

class _ButtonHandler(_ParStyleHandler):
	def __init__(self, ptype, hasvalue=True):
		self.ptype = ptype
		self.hasvalue = hasvalue

	def SpecFromTuplet(self, tuplet, pathprefix=None, metadata=None, **kwargs):
		par = tuplet[0]
		if not metadata:
			metadata = {}
		return ParamSpec(
			par.tupletName,
			ptype=self.ptype,
			label=par.label,
			path=(pathprefix + par.tupletName) if pathprefix else None,
			style=par.style,
			group=par.page.name,
			defaultval=par.default if self.hasvalue else None,
			value=par.eval() if self.hasvalue else None,
			help=metadata.get('help', None),
			offhelp=metadata.get('offhelp', None),
			buttontext=metadata.get('btntext', None),
			buttonofftext=metadata.get('btnofftext', None),
			tags=_GetTagsFromParMetadata(metadata),
		)

class _VectorHandler(_ParStyleHandler):
	def __init__(self, ptype):
		self.ptype = ptype

	def SpecFromTuplet(self, tuplet, pathprefix=None, usenumbers=False, metadata=None, **kwargs):
		if usenumbers:
			partkeys = [str(i) for i in range(1, len(tuplet) + 1)]
			partlabels = partkeys
		else:
			partkeys = tuplet[0].style.lower()
			partlabels = tuplet[0].style
		path = (pathprefix + tuplet[0].tupletName) if pathprefix else None
		parts = [
			_PartFromPar(tuplet[i], partkeys[i], partlabels[i], pathprefix=path)
			for i in range(len(tuplet))
		]
		if not metadata:
			metadata = {}
		return ParamSpec(
			tuplet[0].tupletName,
			label=tuplet[0].label,
			ptype=self.ptype,
			path=path,
			style=tuplet[0].style,
			group=tuplet[0].page.name,
			parts=parts,
			help=metadata.get('help', None),
			tags=_GetTagsFromParMetadata(metadata),
		)

def _PartFromPar(par, key, label, pathprefix=None):
	return ParamPartSpec(
		key,
		label=label,
		defaultval=par.default,
		value=par.eval(),
		minlimit=par.min if par.clampMin else None,
		maxlimit=par.max if par.clampMax else None,
		minnorm=par.normMin,
		maxnorm=par.normMax,
		path=(pathprefix + key) if pathprefix else None,
	)

class _VariableLengthHandler(_ParStyleHandler):
	def __init__(self, singletype, multitype):
		self.singletype = singletype
		self.vechandler = _VectorHandler(multitype)

	def SpecFromTuplet(self, tuplet, pathprefix=None, metadata=None, **kwargs):
		if len(tuplet) > 1:
			return self.vechandler.SpecFromTuplet(tuplet, usenumbers=True, metadata=metadata)
		par = tuplet[0]
		attrs = _NumberAttributesFromPar(par)
		if not metadata:
			metadata = {}
		return ParamSpec(
			par.tupletName,
			ptype=self.singletype,
			label=par.label,
			path=(pathprefix + par.tupletName) if pathprefix else None,
			style=par.style,
			group=par.page.name,
			minlimit=attrs['minlimit'],
			maxlimit=attrs['maxlimit'],
			minnorm=attrs['minnorm'],
			maxnorm=attrs['maxnorm'],
			defaultval=attrs['default'],
			value=attrs['value'],
			help=metadata.get('help', None),
			tags=_GetTagsFromParMetadata(metadata),
		)

class _OtherHandler(_ParStyleHandler):
	def SpecFromTuplet(self, tuplet, pathprefix=None, metadata=None, **kwargs):
		if not metadata:
			metadata = {}
		par = tuplet[0]
		return ParamSpec(
			par.tupletName,
			ptype=ParamType.other,
			label=par.label,
			path=(pathprefix + par.tupletName) if pathprefix else None,
			style=par.style,
			group=par.page.name,
			help=metadata.get('help', None),
			tags=_GetTagsFromParMetadata(metadata),
		)

_parStyleHandlers = {}
_parStyleHandlers['Pulse'] = _ButtonHandler(ParamType.trigger, hasvalue=False)
_parStyleHandlers['Toggle'] = _ButtonHandler(ParamType.bool)
_parStyleHandlers['Str'] = _SimpleHandler(ParamType.string)
_parStyleHandlers['StrMenu'] = _SimpleHandler(ParamType.string, hasoptions=True, hasvalueindex=True)
_parStyleHandlers['Menu'] = _SimpleHandler(ParamType.menu, hasoptions=True, hasvalueindex=True)
_parStyleHandlers['RGB'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['RGBA'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['UV'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['UVW'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['XY'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['XYZ'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['WH'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['Int'] = _VariableLengthHandler(singletype=ParamType.int, multitype=ParamType.ivec)
_parStyleHandlers['Float'] = _VariableLengthHandler(singletype=ParamType.float, multitype=ParamType.fvec)
_otherHandler = _OtherHandler()

ParamMetaKeys = [
	'store',
	'source',
	'advanced',
	'expose',
	'help',
	'offhelp',
	'btntext',
	'btnofftext',
	'mappable',
	'filterable',
	'sequenceable',
]

def _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1, store=1, source=0, advanced=0, expose=1):
	return {
		'mappable': mappable,
		'filterable': filterable,
		'sequenceable': sequenceable,
		'store': store,
		'source': source,
		'advanced': advanced,
		'expose': expose,
		'help': '',
		'offhelp': '',
		'btntext': '',
		'btnofftext': '',
	}

_defaultStyleMetadata = {
	'Pulse': _CreateStyleMetadata(mappable=1, filterable=0, sequenceable=1),
	'Toggle': _CreateStyleMetadata(mappable=1, filterable=0, sequenceable=1),
	'Str': _CreateStyleMetadata(mappable=0, filterable=0, sequenceable=0),
	'StrMenu': _CreateStyleMetadata(mappable=0, filterable=0, sequenceable=0),
	'Menu': _CreateStyleMetadata(mappable=1, filterable=0, sequenceable=1),
	'Int': _CreateStyleMetadata(mappable=1, filterable=0, sequenceable=1),
	'RGB': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'RGBA': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'Float': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'UV': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'UVW': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'XY': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'XYZ': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
	'WH': _CreateStyleMetadata(mappable=1, filterable=1, sequenceable=1),
}
_unsupportedStyleMetadata = _CreateStyleMetadata(mappable=0, filterable=0, sequenceable=0, store=1, source=0, advanced=0, expose=0)
del _CreateStyleMetadata

def GetDefaultMetadataForStyle(style):
	return _defaultStyleMetadata.get(style, _unsupportedStyleMetadata)

def _GetTagsFromParMetadata(metadata):
	if not metadata:
		return []
	return [
		key for key, val in metadata.items() if val in ['1', 1]
	]

def _NumberAttributesFromPar(par):
	return {
		'value': par.eval(),
		'default': par.default,
		'minlimit': par.min if par.clampMin else None,
		'maxlimit': par.max if par.clampMax else None,
		'minnorm': par.normMin,
		'maxnorm': par.normMax,
	}

def _OptionsFromPar(par):
	if not par.menuNames:
		return []
	options = []
	for name, label in zip(par.menuNames, par.menuLabels):
		options.append(ParamOption(key=name, label=label))
	return options

# def _GetTupletAttrs(tuplet, attrname):
# 	if len(tuplet) == 1:
# 		return getattr(tuplet[0], attrname)
# 	return [getattr(p, attrname) for p in tuplet]

def SpecFromParTuplet(tuplet, pathprefix=None, getoptions=None, metadata=None):
	style = tuplet[0].style
	if not metadata:
		metadata = {}
	handler = _parStyleHandlers.get(style, _otherHandler)
	return handler.SpecFromTuplet(tuplet, pathprefix=pathprefix, getoptions=getoptions, metadata=metadata)

# def SpecsFromParTuplets(tuplets, tupletfilter=None, pathprefix=None):
# 	return [
# 		SpecFromParTuplet(t, pathprefix=pathprefix)
# 		for t in _FilterParTuplets(tuplets, tupletfilter)
# 		]

# def SpecsFromParPages(pages, tupletfilter=None, pagefilter=None, pathprefix=None):
# 	specs = []
# 	for page in _FilterByName(pages, pagefilter):
# 		specs += SpecsFromParTuplets(
# 			page.parTuplets,
# 			tupletfilter=tupletfilter,
# 			pathprefix=pathprefix
# 		)
# 	return specs

def BuildModuleSchemas(modules, pathprefix):
	modules = sorted(modules, key=lambda m: m.par.order)
	return [
		m.GetSchema(pathprefix=pathprefix)
		for m in modules
	]

# def _FilterByName(objs, test):
# 	if test is None:
# 		return objs
# 	elif callable(test):
# 		return filter(test, objs)
# 	elif isinstance(test, str):
# 		return filter(lambda o: o.name == test, objs)
# 	else:
# 		return filter(lambda o: o.name in test, objs)

def _FilterParTuplets(tuplets, tupletfilter):
	if tupletfilter is None:
		return tuplets
	elif callable(tupletfilter):
		return filter(tupletfilter, tuplets)
	elif isinstance(tupletfilter, str):
		return filter(lambda t: t[0].name == tupletfilter, tuplets)
	else:
		return filter(lambda t: t[0].name in tupletfilter, tuplets)

class SourceOptionsSupplier:
	def __init__(self, getnodes):
		self.cache = None
		self.getnodes = getnodes

	def __call__(self, *args, **kwargs):
		if self.cache is None:
			self.cache = [
				ParamOption(n['id'], n['label'])
				for n in self.getnodes()
			]
		return self.cache

# NOTE: does NOT generate child modules!
def BuildModuleSchema(module,
                      comp,
                      pathprefix=None,
                      helper=None,
                      tags=None):
	master = comp.par.clone.eval()
	mtype = master.path if master else None
	key = comp.par.Modname.eval()
	path = (pathprefix + comp.path) if pathprefix else None
	parprefix = (path + ':') if path else None
	params, paramgroups = _BuildModuleParamsAndParamGroups(
		module=module,
		comp=comp,
		parprefix=parprefix,
		helper=helper
	)
	return ModuleSpec(
		key=key,
		label=comp.par.Uilabel.eval(),
		path=path,
		moduletype=mtype,
		tags=tags,
		params=params,
		paramgroups=paramgroups,
	)

def BuildModuleTypeSchema(module,
                          comp,
                          helper=None,
                          ):
	parprefix = ':'
	params, paramgroups = _BuildModuleParamsAndParamGroups(
		module=module,
		comp=comp,
		parprefix=parprefix,
		helper=helper
	)
	return ModuleTypeSpec(
		module.path,
		label=comp.par.Uilabel.eval(),
		params=params,
		paramgroups=paramgroups,
	)

def _BuildModuleParamsAndParamGroups(module,
                                     comp,
                                     parprefix=None,
                                     helper=None):
	partuplets = module.GetModParamTuplets(includePulse=True) + [
		comp.par.Bypass.tuplet,
		comp.par.Solo.tuplet,
	]
	includedparamgroups = {t[0].page.name for t in partuplets}
	paramgroups = [
		GroupInfo(
			page.name,
			label=page.name,
			tags=['special'] if page.name == 'Module' else []
		) for page in comp.customPages
		if page.name in includedparamgroups
		]
	params = [
			SpecFromParTuplet(
				t,
				pathprefix=parprefix,
				getoptions=helper.GetParamOptions,
				metadata=helper.GetParamMeta(t[0].tupletName))
			for t in partuplets
		]
	return params, paramgroups


# noinspection PyMethodMayBeStatic
class ModuleSchemaHelper:
	def GetParamFlag(self, name, flag, defval):
		return defval

	def GetParamMeta(self, name):
		return {}

	def GetParamOptions(self, name):
		return None
