print('shell/schema.py initializing')

from enum import Enum
import json

class ParamType(Enum):
	other = 1
	bool = 3
	string = 4
	int = 5
	float = 6
	ivec = 7
	fvec = 8
	menu = 10
	trigger = 11

class _BaseSchemaNode:
	@property
	def JsonDict(self):
		raise NotImplementedError()

	def ToJson(self, **kwargs):
		return json.dumps(self.JsonDict, **kwargs)

	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.JsonDict)

class ParamOption(_BaseSchemaNode):
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def JsonDict(self):
		return {'key': self.key, 'label': self.label}

class ParamSpec(_BaseSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			ptype=ParamType.other,
			othertype=None,
			minlimit=None,
			maxlimit=None,
			minnorm=None,
			maxnorm=None,
			defaultval=None,
			length=None,
			style=None,
			group=None,
			options=None,
			tags=None):
		self.key = key
		self.label = label
		self.ptype = ptype
		self.othertype = othertype
		self.minlimit = minlimit
		self.maxlimit = maxlimit
		self.minnorm = minnorm
		self.maxnorm = maxnorm
		self.defaultval = defaultval
		self.length = length
		self.style = style
		self.group = group
		self.options = options
		self.tags = tags

	@property
	def JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'type': self.ptype.name,
			'othertype': self.othertype,
			'minLimit': self.minlimit,
			'maxLimit': self.maxlimit,
			'minNorm': self.minnorm,
			'maxNorm': self.maxnorm,
			'default': self.defaultval,
			'length': self.length,
			'style': self.style,
			'group': self.group,
			'options': [o.JsonDict for o in self.options] if self.options else None,
			'tags': self.tags,
		})

class ModuleSpec(_BaseSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			moduletype=None,
			group=None,
			tags=None,
			params=None,
			children=None):
		self.key = key
		self.label = label
		self.moduletype = moduletype
		self.group = group
		self.tags = tags
		self.params = params
		self.children = children

	@property
	def JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'moduleType': self.moduletype,
			'group': self.group,
			'tags': self.tags,
			'params': [c.JsonDict for c in self.params] if self.params else None,
			'children': [c.JsonDict for c in self.children] if self.children else None,
		})

class AppSchema(_BaseSchemaNode):
	def __init__(self, key, label=None, description=None, children=None):
		self.key = key
		self.label = label
		self.description = description
		self.children = children or []

	@property
	def JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'description': self.description,
			'children': [c.JsonDict for c in self.children],
		})

def _CleanDict(d):
		for k in list(d.keys()):
			if d[k] is None or d[k] == '':
				del d[k]
		return d

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
			par.name,
			label=par.label,
			ptype=self.ptype,
			style=par.style,
			group=par.page.name,
			defaultval=par.default if self.hasdefault else None,
			options=_OptionsFromPar(par) if self.hasoptions else None)

class _VectorHandler(_ParStyleHandler):
	def __init__(self, ptype):
		self.ptype = ptype

	def SpecFromTuplet(self, tuplet):
		attrs = [_NumberAttributesFromPar(p) for p in tuplet]
		return ParamSpec(
			tuplet[0].name,
			ptype=self.ptype,
			style=tuplet[0].style,
			group=tuplet[0].page.name,
			length=len(tuplet),
			minlimit=[a['minlimit'] for a in attrs],
			maxlimit=[a['maxlimit'] for a in attrs],
			minnorm=[a['minnorm'] for a in attrs],
			maxnorm=[a['maxnorm'] for a in attrs],
			defaultval=[a['default'] for a in attrs])

class _VariableLengthHandler(_ParStyleHandler):
	def __init__(self, singletype, multitype):
		self.singletype = singletype
		self.vechandler = _VectorHandler(multitype)

	def SpecFromTuplet(self, tuplet):
		if len(tuplet) > 1:
			return self.vechandler.SpecFromTuplet(tuplet)
		par = tuplet[0]
		attrs = _NumberAttributesFromPar(par)
		return ParamSpec(
			par.name,
			label=par.label,
			style=par.style,
			group=par.page.name,
			minlimit=attrs['minlimit'],
			maxlimit=attrs['maxlimit'],
			minnorm=attrs['minnorm'],
			maxnorm=attrs['maxnorm'],
			defaultval=attrs['default'])

_parStyleHandlers = {}
_parStyleHandlers['Pulse']= _SimpleHandler(ParamType.trigger, hasdefault=False)
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

def _SpecsFromParTuplets(tuplets, tupletfilter=None):
	return [_SpecFromParTuplet(t) for t in _FilterParTuplets(tuplets, tupletfilter)]

def SpecsFromParPages(pages, tupletfilter=None, pagefilter=None):
	specs = []
	for page in _FilterByName(pages, pagefilter):
		specs += _SpecsFromParTuplets(page.parTuplets, tupletfilter=tupletfilter)
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
