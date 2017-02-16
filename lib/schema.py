print('shell/schema.py initializing')

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

import sys
# _pytctrlpath = op('/_').var('shelldir')
_pytctrlpath = project.folder
_pytctrlpath = _pytctrlpath.replace('/', '\\')
if not _pytctrlpath.endswith('\\'):
	_pytctrlpath += '\\'
_pytctrlpath += 'pytctrl'
if _pytctrlpath not in sys.path:
	sys.path.append(_pytctrlpath)

# export these so this module acts as a proxy
from tctrl.schema import ParamType, ParamOption, ParamPartSpec, ParamSpec, ModuleSpec, AppSchema

class _ParStyleHandler:
	def SpecFromTuplet(self, tuplet): pass

class _SimpleHandler(_ParStyleHandler):
	def __init__(self, ptype, hasoptions=False, hasdefault=True):
		self.ptype = ptype
		self.hasoptions = hasoptions
		self.hasdefault = hasdefault

	def SpecFromTuplet(self, tuplet):
		par = tuplet[0]
		return ParamSpec(
			par.tupletName,
			label=par.label,
			ptype=self.ptype,
			style=par.style,
			group=par.page.name,
			defaultval=par.default if self.hasdefault else None,
			options=_OptionsFromPar(par) if self.hasoptions else None)

class _VectorHandler(_ParStyleHandler):
	def __init__(self, ptype):
		self.ptype = ptype

	def SpecFromTuplet(self, tuplet, usenumbers=False):
		if usenumbers:
			partkeys = list(range(1, len(tuplet) + 1))
			partlabels = partkeys
		else:
			partkeys = tuplet[0].style.lower()
			partlabels = tuplet[0].style
		parts = [
			_PartFromPar(tuplet[i], partkeys[i], partlabels[i])
			for i in range(len(tuplet))
		]
		return ParamSpec(
			tuplet[0].tupletName,
			label=tuplet[0].label,
			ptype=self.ptype,
			style=tuplet[0].style,
			group=tuplet[0].page.name,
			length=len(tuplet),
			parts=parts)

def _PartFromPar(par, key, label):
	return ParamPartSpec(
		key,
		label=label,
		defaultval=par.default,
		minlimit=par.min if par.clampMin else None,
		maxlimit=par.max if par.clampMax else None,
		minnorm=par.normMin,
		maxnorm=par.normMax,
	)

class _VariableLengthHandler(_ParStyleHandler):
	def __init__(self, singletype, multitype):
		self.singletype = singletype
		self.vechandler = _VectorHandler(multitype)

	def SpecFromTuplet(self, tuplet):
		if len(tuplet) > 1:
			return self.vechandler.SpecFromTuplet(tuplet, usenumbers=True)
		par = tuplet[0]
		attrs = _NumberAttributesFromPar(par)
		return ParamSpec(
			par.tupletName,
			label=par.label,
			style=par.style,
			group=par.page.name,
			minlimit=attrs['minlimit'],
			maxlimit=attrs['maxlimit'],
			minnorm=attrs['minnorm'],
			maxnorm=attrs['maxnorm'],
			defaultval=attrs['default'])

_parStyleHandlers = {}
_parStyleHandlers['Pulse'] = _SimpleHandler(ParamType.trigger, hasdefault=False)
_parStyleHandlers['Toggle'] = _SimpleHandler(ParamType.bool)
_parStyleHandlers['Str'] = _SimpleHandler(ParamType.string)
_parStyleHandlers['StrMenu'] = _SimpleHandler(ParamType.string, hasoptions=True)
_parStyleHandlers['Menu'] = _SimpleHandler(ParamType.menu, hasoptions=True)
_parStyleHandlers['RGB'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['RGBA'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['UV'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['UVW'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['XY'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['XYZ'] = _VectorHandler(ParamType.fvec)
_parStyleHandlers['Int'] = _VariableLengthHandler(singletype=ParamType.int, multitype=ParamType.ivec)
_parStyleHandlers['Float'] = _VariableLengthHandler(singletype=ParamType.float, multitype=ParamType.fvec)

def _NumberAttributesFromPar(par):
	return {
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

def _GetTupletAttrs(tuplet, attrname):
	if len(tuplet) == 1:
		return getattr(tuplet[0], attrname)
	return [getattr(p, attrname) for p in tuplet]

def _SpecFromParTuplet(tuplet):
	style = tuplet[0].style
	if style not in _parStyleHandlers:
		return ParamSpec(
			tuplet[0].tupletName,
			label=tuplet[0].label,
			ptype=ParamType.other,
			style=style,
			group=tuplet[0].page.name)
	handler = _parStyleHandlers[style]
	return handler.SpecFromTuplet(tuplet)

def SpecsFromParTuplets(tuplets, tupletfilter=None):
	return [_SpecFromParTuplet(t) for t in _FilterParTuplets(tuplets, tupletfilter)]

def SpecsFromParPages(pages, tupletfilter=None, pagefilter=None):
	specs = []
	for page in _FilterByName(pages, pagefilter):
		specs += SpecsFromParTuplets(page.parTuplets, tupletfilter=tupletfilter)
	return specs

def _FilterByName(objs, test):
	if test is None:
		return objs
	elif callable(test):
		return filter(test, objs)
	elif isinstance(test, str):
		return filter(lambda o: o.name == test, objs)
	else:
		return filter(lambda o: o.name in test, objs)

def _FilterParTuplets(tuplets, tupletfilter):
	if tupletfilter is None:
		return tuplets
	elif callable(tupletfilter):
		return filter(tupletfilter, tuplets)
	elif isinstance(tupletfilter, str):
		return filter(lambda t: t[0].name == tupletfilter, tuplets)
	else:
		return filter(lambda t: t[0].name in tupletfilter, tuplets)
