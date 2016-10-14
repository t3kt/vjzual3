print('common/util.py initializing')

try:
	import td
except ImportError:
	try:
		from _stubs import td
	except ImportError:
		try:
			from common.lib._stubs import td
		except ImportError:
			td = object()
if False:
	try:
		from _stubs import op
	except ImportError:
		op = object()


import json
import datetime
# import logging
#
# logging.basicConfig(format='%(asctime)s %(message)s')
# logger = logging.getLogger('tdapp')
# logger.setLevel(logging.INFO)

def _interp(x, inrange, outrange):
	return ((outrange[1]-outrange[0])*(x-inrange[0])/(inrange[1]-inrange[0])) + outrange[0]

try:
  from numpy import interp
except ImportError:
  interp = _interp

# class Logger:
# 	def __init__(self, comp):
# 		self.comp = comp
# 		self.buffer = comp.op('./buffer')
#
# 	@property
# 	def _FilePath(self):
# 		path = self.comp.par.Folder.eval() or self.comp.par.Folder.default
# 		if not path.endswith('/'):
# 			path += '/'
# 		path += self.comp.par.Fileprefix.eval() or self.comp.par.Fileprefix.default or ''
# 		return self._TimestampClean + '.log'
#
# 	@property
# 	def _Timestamp(self):
# 		return datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
#
# 	@property
# 	def _TimestampClean(self):
# 		return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
#
# 	def ClearBuffer(self):
# 		self.buffer.text = ''
#
# 	def FlushToFile(self):
# 		path = self._FilePath
# 		if not self.buffer.text:
# 			# nothing to flush
# 			return
# 		self.buffer.save(path)
# 		self.ClearBuffer()
#
# 	def Log(self, message, verbose=False, skipfile=False, skipconsole=False):
# 		if self.comp.par.Silent:
# 			return
# 		if verbose and not self.comp.par.Verbose:
# 			return
# 		text = '[%s] %s' % (self._Timestamp, message)
# 		if not skipconsole:
# 			print(text)
# 		if skipfile or (verbose and not self.comp.par.Verbosetofile):
# 			return
# 		print(text, file=self.buffer)

def Log(msg):
	#logger.info('%s', msg)
	print('[%s]' % datetime.datetime.now().strftime('%m.%d %H:%M:%S'), msg)

def dumpobj(obj, underscores=False, methods=False):
	print('Dump %r type: %r' % (obj, type(obj)))
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
	_ProcessClones(master, lambda c: print('  ' + c.path), predicate=predicate)

class TableMenuSource:
	def __init__(self, dat, nameCol='name', labelCol='label'):
		self.dat = dat
		self.nameCol = nameCol
		self.labelCol = labelCol

	def _GetCol(self, name):
		if not self.dat:
			return []
		cells = self.dat.col(name)
		return [x.val for x in cells[1:]] if cells else []

	@property
	def menuNames(self):
		return self._GetCol(self.nameCol)

	@property
	def menuLabels(self):
		return self._GetCol(self.labelCol)

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
	else:
		for sep in [',', ' ']:
			if sep in val:
				return [v.strip() for v in val.split(sep) if v.strip()]
		return [val]

def ToJson(val):
	return json.dumps(val)

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

def ParseFloat(text, defaultVal=None):
	try:
		return float(text)
	except ValueError:
		return defaultVal

def _AddParsToTable(dat, *pars, quotestrings=False):
	for par in pars:
		if quotestrings and (par.isString or par.isMenu):
			val = repr(par.eval())
		else:
			val = par.eval()
		dat.appendRow([par.name, val])

def CopyParPagesToTable(dat, *pages, quotestrings=False):
	dat.clear()
	for page in pages:
		_AddParsToTable(dat, *page.pars, quotestrings=quotestrings)

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
