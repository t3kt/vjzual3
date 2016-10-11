import json
if False:
	from _stubs import *
try:
	import common_base as base
except ImportError:
	import base

util = base.util
interp = util.interp

print('common tools.py initializing')

def GetActiveEditor():
	pane = ui.panes.current
	if pane.type == PaneType.NETWORKEDITOR:
		return pane
	for pane in ui.panes:
		if pane.type == PaneType.NETWORKEDITOR:
			return pane

def _getTargetPane():
	return GetActiveEditor()

def NavigateTo(path):
	pane = _getTargetPane()
	if not pane:
		return
	target = op(path)
	if not target:
		return
	pane.owner = target

def _getSelected():
	pane = _getTargetPane()
	if not pane:
		return
	selected = pane.owner.selectedChildren
	if not selected:
		selected = [pane.owner.currentChild]
	return selected

def _doOnSelectedOrContext(action):
	selected = _getSelected()
	initedAny = False
	for o in selected:
		if action(o):
			initedAny = True
	if not initedAny:
		pane = _getTargetPane()
		comp = pane.owner
		while comp:
			if action(comp):
				return
			comp = comp.parent()

def _tryInit(o):
	if not o:
		return False
	if o.isDAT and o.name == 'init':
		init = o
	elif o.isCOMP:
		init = o.op('init')
	else:
		init = None
	if not init or not init.isDAT:
		return False
	try:
		ui.status = 'running initializer ' + init.path
		init.run()
	except Exception as e:
		print('INIT error [' + init.path + ']: ' + str(e))
	return True

def InitSelectedOrContext():
	_doOnSelectedOrContext(_tryInit)

def _saveTox(comp):
	if not comp or not comp.isCOMP:
		return False
	toxfile = comp.par.externaltox.eval()
	if not toxfile:
		return False
	comp.save(toxfile)
	ui.status = 'Saved TOX %s to %s' % (comp.path, toxfile)
	return True

def SaveToxSelectedOrContext(ancestors=False):
	if not ancestors:
		_doOnSelectedOrContext(_saveTox)
	else:
		allcomps = dict()
		selected = _getSelected()
		for o in selected:
			if not o.isCOMP:
				continue
			allcomps[o.path] = o
		if not allcomps:
			pane = _getTargetPane()
			allcomps[pane.owner.path] = pane.owner
		for o in list(allcomps.values()):
			i = 1
			while True:
				p = o.parent(i)
				if not p or p.path in allcomps:
					break
				allcomps[p.path] = p
				i += 1
		for o in allcomps.values():
			_saveTox(o)

_orderAxes = {
	'x': {'attr': 'nodeX', 'reverse': False},
	'y': {'attr': 'nodeY', 'reverse': True},
}

def _setAlignOrderBy(sortAttrName, reverseDir):
	selected = _getSelected()
	n = len(selected)
	selected = sorted(
		selected,
		key=lambda o: getattr(o, sortAttrName),
		reverse=reverseDir)
	for i in range(n):
		if hasattr(selected[i].par, 'order'):
			val = interp(float(i), [0, n - 1], [0.0, 1.0])
			selected[i].par.order = val

def SetAlignOrderBy(axis):
	_setAlignOrderBy(_orderAxes[axis]['attr'], _orderAxes[axis]['reverse'])

def CopySelectedPaths():
	sel = _getSelected()
	ui.clipboard = ' '.join([o.path for o in sel])

def ReloadDATs(dats):
	for dat in dats:
		if not dat or not dat.isDAT or not hasattr(dat.par, 'reload'):
			print('ReloadDATs - Cannot reload unsupported OP: ' + dat.path if dat else '_none_')
		else:
			print('ReloadDATs - Reloading DAT: ' + dat.path)
			dat.par.reload.pulse(1)

def DestroyPars(parnames):
	selected = _getSelected()
	if len(parnames) == 1 and parnames[0] == '*':
		print('destroy all pars', selected)
		for o in selected:
			while len(o.customPages) > 0:
				o.customPages.pop().destroy()
	else:
		print('destroyPars', parnames, selected)
		for o in selected:
			oPars = o.pars(*parnames)
			for p in oPars:
				if p.isCustom:
					p.destroy()

def AddTags(tags):
	tags = set(tags)
	selected = _getSelected()
	print('addTags', tags, selected)
	for o in selected:
		o.tags |= tags

def RemoveTags(tags):
	if len(tags) == 1 and tags[0] == '*':
		tags = None
	else:
		tags = set(tags)
	selected = _getSelected()
	print('removeTags', tags if tags else '*', selected)
	for o in selected:
		if tags:
			o.tags -= tags
		else:
			o.tags.clear()

def _getMiddle(vals):
	low, high = min(vals), max(vals)
	return low + (high - low) / 2

class NodeEdge:
	def __init__(self, attrName, calc):
		self.attrName = attrName
		self.calc = calc
	def get(self, o):
		return getattr(o, self.attrName)
	def set(self, o, val):
		setattr(o, self.attrName, val)
	def align(self, os):
		vals = [self.get(o) for o in os]
		newval = self.calc(vals)
		for o in os:
			self.set(o, newval)

class DerivedNodeEdge(NodeEdge):
	def __init__(self, baseAttr, sizeAttr, calc):
		NodeEdge.__init__(self, baseAttr, calc)
		self.sizeAttr = sizeAttr
	def get(self, o):
		return getattr(o, self.attrName) + getattr(o, self.sizeAttr)
	def set(self, o, val):
		setattr(o, self.attrName, val - getattr(o, self.sizeAttr))

nodeEdges = {
	'left': NodeEdge('nodeX', min),
	'top': NodeEdge('nodeY', max),
	'center': NodeEdge('nodeCenterX', _getMiddle),
	'middle': NodeEdge('nodeCenterY', _getMiddle),
	'right': DerivedNodeEdge('nodeX', 'nodeWidth', max),
	'bottom': DerivedNodeEdge('nodeY', 'nodeHeight', min)
}

def Align(dirName):
	selected = _getSelected()
	if len(selected) < 2:
		return
	edge = nodeEdges[dirName]
	edge.align(selected)

def Distribute(axis):
	if axis == 'x':
		attr = 'nodeX'
	else:
		attr = 'nodeY'
	selected = _getSelected()
	n = len(selected)
	if n < 3:
		return
	vals = [getattr(o, attr) for o in selected]
	minVal, maxVal = min(vals), max(vals)
	selected = sorted(
		selected,
		key=lambda o: getattr(o, attr))
	for i in range(n):
		val = interp(float(i), [0, n - 1], [minVal, maxVal])
		setattr(selected[i], attr, round(val))

def SortByName(axis):
	attr = _orderAxes[axis]['attr']
	reverse = _orderAxes[axis]['reverse']
	selected = _getSelected()
	n = len(selected)
	if n < 2:
		return
	vals = [getattr(o, attr) for o in selected]
	minVal, maxVal = min(vals), max(vals)
	selected = sorted(
		selected,
		key=lambda o: o.name,
		reverse=reverse)
	for i in range(n):
		val = interp(float(i), [0, n - 1], [minVal, maxVal])
		setattr(selected[i], attr, round(val))

def ApplyAutoWidth(comp):
	if comp.python:
		raise NotImplementedError('python auto width not yet supported')
	else:
		comp.par.w.expr = "par(opparent('.', 0) + '/panelw')"

def ApplyAutoHeight(comp):
	if comp.python:
		raise NotImplementedError('python auto height not yet supported')
	else:
		comp.par.h.expr = "par(opparent('.', 0) + '/panelh')"

class ToolsExt(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	def PerformAction(self, cmd):
		self._LogEvent('PerformAction(%r)' % cmd)
		if cmd.startswith('Align'):
			Align(cmd.replace('Align', ''))
		elif cmd.startswith('Orderby'):
			SetAlignOrderBy(cmd.replace('Orderby', ''))
		elif cmd.startswith('Distribute'):
			Distribute(cmd.replace('Distribute', ''))
		elif cmd.startswith('Sort'):
			SortByName(cmd.replace('Sort', ''))
		elif cmd == 'Initselected':
			InitSelectedOrContext()
		elif cmd == 'Reloadcode':
			patterns = self.comp.par.Codeops.eval().split(' ')
			ReloadDATs(ops(*patterns))
		elif cmd == 'Reloadconfig':
			patterns = self.comp.par.Configops.eval().split(' ')
			ReloadDATs(ops(*patterns))
		elif cmd == 'Deletepars':
			DestroyPars(self.comp.par.Parstodelete.eval().split(' '))
		elif cmd == 'Addtags':
			AddTags(self.comp.par.Tagstomodify.eval().split(' '))
		elif cmd == 'Removetags':
			RemoveTags(self.comp.par.Tagstomodify.eval().split(' '))
		elif cmd == 'Copypaths':
			CopySelectedPaths()
		elif cmd == 'Savetox':
			SaveToxSelectedOrContext()
		elif cmd == 'Savetoxancestors':
			SaveToxSelectedOrContext(ancestors=True)
		else:
			raise Exception('unrecognized action: ' + cmd)

	def LoadLauncherSpecs(self, table):
		jsonstr = self.comp.par.Launcherspecjson.eval()
		if not jsonstr:
			jsonstr = self.comp.op('default_launcher_specs_json').text
		try:
			_FillTableFromJson(
				table, jsonstr,
				cols=['label', 'path', 'mode'],
				defaults={'mode': 'panel'})
		except ValueError as e:
			raise Exception('tools.LoadLauncherSpecs - error parsing spec json: %s' % (e,))

	def LoadNavigatorSpecs(self, table):
		jsonstr = self.comp.par.Navspecjson.eval()
		if not jsonstr:
			jsonstr = self.comp.op('default_nav_specs_json').text
		try:
			_FillTableFromJson(
				table, jsonstr,
				cols=['label', 'path'],
				defaults={})
		except ValueError as e:
			raise Exception('tools.LoadNavigatorSpecs - error parsing spec json: %s' % (e,))

	def OnLaunchButtonClick(self, button):
		specs = self.comp.op('launcher_specs')
		i = button.digits
		path = specs[i, 'path'].val
		mode = specs[i, 'mode'].val
		o = op(path)
		if not o:
			raise Exception('tools.OnLaunchButtonClick - path not found: %r' % (path,))
		if mode == 'window':
			o.par.winopen.pulse()
		elif mode == 'panel':
			o.openViewer()
		elif mode == 'borderless':
			o.openViewer(borders=False)
		else:
			raise Exception('tools.OnLaunchButtonClick - unrecognized launch mode: %r' % (mode,))

	def OnLaunchCellClick(self, i):
		specs = self.comp.op('launcher_specs')
		path = specs[i, 'path'].val
		mode = specs[i, 'mode'].val
		o = op(path)
		if not o:
			raise Exception('tools.OnLaunchCellClick - path not found: %r' % (path,))
		if mode == 'window':
			o.par.winopen.pulse()
		elif mode == 'panel':
			o.openViewer()
		elif mode == 'borderless':
			o.openViewer(borders=False)
		else:
			raise Exception('tools.OnLaunchCellClick - unrecognized launch mode: %r' % (mode,))

	def OnNavigatorButtonClick(self, button):
		specs = self.comp.op('nav_specs')
		i = button.digits
		path = specs[i, 'path'].val
		if not op(path):
			raise Exception('tools.OnNavigatorButtonClick - path not found: %r' % (path,))
		NavigateTo(path)

	def OnNavigatorCellClick(self, i):
		specs = self.comp.op('nav_specs')
		path = specs[i, 'path'].val
		if not op(path):
			raise Exception('tools.OnNavigatorCellClick - path not found: %r' % (path,))
		NavigateTo(path)

def _FillTableFromJson(table, jsonstr, cols, defaults):
	table.clear()
	table.appendRow(cols)
	items = json.loads(jsonstr)
	for item in items:
		table.appendRow([
			item.get(col, defaults.get('col', ''))
			for col in cols
		])
