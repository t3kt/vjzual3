if False:
	from _stubs import *

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

def SaveToxSelectedOrContext():
	_doOnSelectedOrContext(_saveTox)

def ReloadDATs(dats):
	for dat in dats:
		if not dat.isDAT or not hasattr(dat.par, 'reload'):
			print('Cannot reload unsupported OP: ' + dat.path)
		else:
			print('Reloading DAT: ' + dat.path)
			dat.par.reload.pulse(1)

class ToolsExt:
	def __init__(self, comp):
		self.comp = comp
