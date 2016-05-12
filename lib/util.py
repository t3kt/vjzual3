print('core/util.py initializing')

try:
	import td
except ImportError:
	from _stubs import td

import json
import datetime

from numpy import interp

def Log(*args):
	print('[%s]' % datetime.datetime.now().strftime('%m.%d %H:%M:%S'), *args)

def dumpobj(obj, underscores=False, methods=False):
	print('Dump ' + repr(obj) + ' type:' + repr(type(obj)))
	if isinstance(obj, (list, tuple)):
		for i in range(len(obj)):
			print('  [' + str(i) + ']: ' + repr(obj[i]))
	else:
		for key in dir(obj):
			if key.startswith('_') and not underscores:
				continue
			try:
				val = getattr(obj, key)
			except Exception as e:
				print('  ' + key + ': [ERROR]', e)
				continue
			if callable(val) and not methods:
				continue
			print('  ' + key + ': ' + repr(val))


def setattrs(obj, **attrs):
	if isinstance(obj, (tuple, list)):
		for o in obj:
			setattrs(o, **attrs)
	else:
		for key in attrs:
			setattr(obj, key, attrs[key])

def _ProcessClones(master, action, predicate=None):
	if not master or not hasattr(master, 'clones'):
		return
	for c in master.clones:
		if predicate is not None and not predicate(c):
			continue
		action(c)

def DumpClones(master, predicate=None):
	print('Clones of ' + master.path)
	_ProcessClones(master, lambda c: print('  ' + c.path), predicate=predicate)

class TableMenuSource:
	def __init__(self, dat, nameCol='name', labelCol='label'):
		self.dat = dat
		self.nameCol = nameCol
		self.labelCol = labelCol

	@property
	def menuNames(self):
		return [x.val for x in self.dat.col(self.nameCol)[1:]]

	@property
	def menuLabels(self):
		return [x.val for x in self.dat.col(self.labelCol)[1:]]

def GetVisibleCOMPsHeight(comps):
	return sum([o.par.h for o in comps if getattr(o, 'isPanel', False) and o.par.display])

def GetVisibleChildCOMPsHeight(parentOp):
	return GetVisibleCOMPsHeight([c.owner for c in parentOp.outputCOMPConnectors[0].connections])

def GetOrAddCell(dat, row, col):
	if dat[row, col] is None:
		if not dat.row(row):
			dat.appendRow([row])
		if not dat.col(col):
			dat.appendCol([col])
	return dat[row, col]

def ParseStringList(val):
	if not val:
		return []
	if val.startswith('['):
		return json.loads(val)
	elif ',' in val:
		return [v.strip() for v in val.split(',') if v.strip()]
	else:
		return [val]

def IsTupleOrList(val):
	return isinstance(val, (tuple, list))

def CopyParOpts(frompars, topars, includeMenuSource=False, includeLabel=True):
	# Log('CopyParOpts(frompars=%r, topars=%r, ...)' % (frompars, topars))
	if not IsTupleOrList(frompars):
		frompars = [frompars] * (len(topars) if IsTupleOrList(topars) else 1)
	if not IsTupleOrList(topars):
		topars = [topars] * len(frompars)
	# Log('CopyParOpts() .. after arg preproc: frompars=%r, topars=%r' % (frompars, topars))
	for frompar, topar in zip(frompars, topars):
		attrs = []
		if includeLabel:
			attrs += ['label']
		if topar.isNumber:
			attrs += ['min', 'max', 'normMin', 'normMax', 'clampMin', 'clampMax']
		if topar.isMenu:
			attrs += ['menuNames', 'menuLabels']
			if includeMenuSource:
				attrs += ['menuSource']
		attrs += ['default']
		for attrname in attrs:
			try:
				setattr(topar, attrname, getattr(frompar, attrname))
			except td.error as e:
				Log('CopyParOpts() .. unable to set %s on %r from %r - %r' % (attrname, topar, frompar, e))
	return topars

def CopyPar(page, sourceOp, label, style, labelPrefix='', menuSourcePath='', namePrefix='', sourceName=None, name=None, size=None, fromPattern=None, defaultVal=None):
	# Log('CopyPar(page=%r, sourceOp=%r, label=%r, style=%r, labelPrefix=%r, menuSourcePath=%r, namePrefix=%r, sourceName=%r, name=%r, size=%r, fromPattern=%r, defaultVal=%r)' % (
	# 	page, sourceOp, label, style, labelPrefix, menuSourcePath, namePrefix, sourceName, name, size, fromPattern, defaultVal))
	if not sourceName:
		sourceName = label.replace(' ', '').replace('-', '').lower()
	if not name:
		name = sourceName
	appendkwargs = {'label': labelPrefix + label}
	if size is not None:
		appendkwargs['size'] = size
	attrs = {}
	if style == 'Menu' and menuSourcePath:
		attrs['menuSource'] = "op(%r).par.%s" % (menuSourcePath, sourceName if sourceName else name)
	if defaultVal is not None:
		attrs['default'] = defaultVal
	if not fromPattern:
		fromPattern = [sourceName]
	elif not IsTupleOrList(fromPattern):
		fromPattern = [fromPattern]
	if namePrefix:
		name = namePrefix + name.lower()
	else:
		name = name.capitalize()
	setattrs(
		CopyParOpts(
			sourceOp.pars(*fromPattern),
			getattr(page, 'append' + style)(name, **appendkwargs),
			includeLabel=False),
		**attrs)

def MergeDicts(*dicts):
	out = dict()
	for d in dicts:
		out.update(d)
	return out

_EXPORTS = {
	'dumpobj': dumpobj,
	'setattrs': setattrs,
	'DumpClones': DumpClones,
}

def EXPORT(console_locals):
	"""Export utility functions to the console.
	Usage: op.core.mod.core_utils.EXPORT(locals())
	:param console_locals: dict of local variables to export into
	"""
	console_locals.update(_EXPORTS)
