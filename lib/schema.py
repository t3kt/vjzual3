print('shell/schema.py initializing')

from enum import Enum
import json

class ParamType(Enum):
	unknown = 0
	other = 1
	bool = 3
	string = 4
	int = 5
	float = 6
	ivec = 7
	fvec = 8
	bvec = 9
	menu = 10
	trigger = 11

class ParamOption:
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def _JsonDict(self):
		return {'key': self.key, 'label': self.label}

	def ToJson(self):
		return json.dumps(self._JsonDict)

class ParamSpec:
	def __init__(self,
	             key,
	             label=None,
	             ptype=ParamType.unknown,
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
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'type': self.ptype.name,
			'minLimit': self.minlimit,
			'maxLimit': self.maxlimit,
			'minNorm': self.minnorm,
			'maxNorm': self.maxnorm,
			'default': self.defaultval,
			'length': self.length,
			'style': self.style,
			'group': self.group,
			'options': [o._JsonDict for o in self.options] if self.options else None,
			'tags': self.tags,
		})

	def __repr__(self):
		return 'ParamSpec(%r)' % self._JsonDict

	def ToJson(self):
		return json.dumps(self._JsonDict)

class ModuleSpec:
	def __init__(self,
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
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'moduleType': self.moduletype,
			'group': self.group,
			'tags': self.tags,
			'params': [c._JsonDict for c in self.params] if self.params else None,
			'children': [c._JsonDict for c in self.children] if self.children else None,
		})

	def __repr__(self):
		return 'ModuleSpec(%r)' % self._JsonDict

	def ToJson(self):
		return json.dumps(self._JsonDict)

class AppSchema:
	def __init__(self, key, label=None, description=None, children=None):
		self.key = key
		self.label = label
		self.description = description
		self.children = children or []

	@property
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'description': self.description,
			'children': [c._JsonDict for c in self.children],
		})

	def __repr__(self):
		return 'AppSchema(%r)' % self._JsonDict

	def ToJson(self):
		return json.dumps(self._JsonDict)

def _CleanDict(d):
		for k in list(d.keys()):
			if d[k] is None or d[k] == '':
				del d[k]
		return d

class _ParStyleProps:
	def __init__(self,
	             ptype,
	             hasrange=False,
	             haslength=False,
	             fixedlength=None,
	             hasoptions=False):
		self.ptype = ptype
		self.hasrange = hasrange
		self.haslength = haslength or fixedlength is not None
		self.fixedlength = fixedlength
		self.hasoptions = hasoptions

_parStyleProps = {
	'Str': _ParStyleProps(ParamType.string),
	'StrMenu': _ParStyleProps(ParamType.string, hasoptions=True),
	'Float': _ParStyleProps(ParamType.float, hasrange=True, haslength=True),
	'Int': _ParStyleProps(ParamType.int, hasrange=True, haslength=True),
	'Toggle': _ParStyleProps(ParamType.bool),
	'Pulse': _ParStyleProps(ParamType.trigger),
	'Menu': _ParStyleProps(ParamType.menu, hasoptions=True),
	'RGB': _ParStyleProps(ParamType.fvec, hasrange=True, fixedlength=3),
	'RGBA': _ParStyleProps(ParamType.fvec, hasrange=True, fixedlength=4),
	'UV': _ParStyleProps(ParamType.fvec, hasrange=True, fixedlength=2),
	'UVW': _ParStyleProps(ParamType.fvec, hasrange=True, fixedlength=3),
	'XY': _ParStyleProps(ParamType.fvec, hasrange=True, fixedlength=2),
	'XYZ': _ParStyleProps(ParamType.fvec, hasrange=True, fixedlength=3),
}

def _GetTupletAttrs(tuplet, attrname):
	if len(tuplet) == 1:
		return getattr(tuplet[0], attrname)
	return [getattr(p, attrname) for p in tuplet]

def _SpecFromParTuplet(tuplet):
	style = tuplet[0].style
	if style not in _parStyleProps:
		return ParamSpec(tuplet[0].tupletName,
		                 label=tuplet[0].label,
		                 ptype=ParamType.other,
		                 style=style,
		                 group=tuplet[0].page.name)
	styleProps = _parStyleProps[style]
	options = None
	if styleProps.hasoptions:
		options = []
		for name, label in zip(tuplet[0].menuNames, tuplet[0].menuLabels):
			options.append(ParamOption(key=name, label=label))
	return ParamSpec(
		tuplet[0].tupletName,
		label=tuplet[0].label,
		ptype=styleProps.ptype,
		minlimit=_GetTupletAttrs(tuplet, 'min') if styleProps.hasrange and tuplet[0].clampMin else None,
		maxlimit=_GetTupletAttrs(tuplet, 'max') if styleProps.hasrange and tuplet[0].clampMax else None,
		minnorm=_GetTupletAttrs(tuplet, 'normMin') if styleProps.hasrange else None,
		maxnorm=_GetTupletAttrs(tuplet, 'normMax') if styleProps.hasrange else None,
		defaultval=_GetTupletAttrs(tuplet, 'default'),
		length=len(tuplet),
		style=style,
		group=tuplet[0].page.name,
		options=options)

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
