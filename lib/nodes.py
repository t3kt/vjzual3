print('shell/nodes.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base

try:
	import common_ctrl as ctrl
except ImportError:
	try:
		import ctrl
	except ImportError:
		import common.lib.ctrl as ctrl

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

DropMenu = ctrl.DropMenu

class NodeSelectorPopup(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		# self._Nodes = comp.op('./data_nodes')
		# self._List = comp.op('./data_node_list')
		# self._ListSettings = comp.op('./list_settings')

	def Initialize(self, targetop, targetpar, nodetype='video'):
		self.comp.par.Targetop = targetop
		self.comp.par.Targetpar = targetpar
		self.comp.par.Nodetype = nodetype

	@property
	def _Nodes(self):
		return self.comp.op('./data_nodes')

	@property
	def _List(self):
		return self.comp.op('./node_list')

	@property
	def _ListSettings(self):
		return self.comp.op('./list_settings')

	@property
	def _SelectedRowIndex(self):
		selid = self.comp.par.Selnodeid.eval()
		if not selid:
			return None
		cell = self._Nodes[selid, 'id']
		return cell.row if cell is not None else None

	@property
	def _TargetPar(self):
		targetop = self.comp.par.Targetop.eval()
		if not targetop:
			return None
		parname = self.comp.par.Targetpar.eval()
		if not parname:
			return None
		pars = targetop.pars(parname)
		return pars[0] if pars else None

	def _SelectRow(self, row):
		nodetype = self._GetRowAttr(row, 'nodetype')
		if nodetype != 'data':
			return
		selid = self._GetRowId(row) or ''
		self.comp.par.Selnodeid.val = selid
		self._PushValue()

	def _PushValue(self):
		selid = self.comp.par.Selnodeid.val
		par = self._TargetPar
		if par is None:
			return
		par.val = selid

	def _GetRowId(self, row):
		return self._GetRowAttr(row, 'id')

	def _GetRowAttr(self, row, name):
		nodes = self._Nodes
		if not row or row == -1 or row >= nodes.numRows:
			return None
		return nodes[row, name].val

	def LoadValueFromTarget(self):
		par = self._TargetPar
		if par is None:
			return
		self.comp.par.Selnodeid.val = par.eval()
		self._UpdateRowHighlights()

	# def _SelectPrevious(self):
	# 	selrow = self._SelectedRowIndex or 0
	# 	if selrow < 2:
	# 		return
	# 	newid = self._GetRowId(selrow - 1)
	# 	if newid:
	# 		self.comp.par.Selnodeid = newid
	#
	# def _SelectNext(self):
	# 	selrow = self._SelectedRowIndex or 0
	# 	if selrow >= (self._Nodes.numRows - 1):
	# 		return
	# 	if selrow == 0:
	# 		newrow = 1
	# 	else:
	# 		newrow = selrow + 1
	# 	newid = self._GetRowId(newrow)
	# 	if newid:
	# 		self.comp.par.Selnodeid = newid
	#
	# def OnKeyEvent(self, key):
	# 	if key == 'up':
	# 		self._SelectPrevious()
	# 	elif key == 'down':
	# 		self._SelectNext()

	def List_onInitCell(self, row, col, attribs):
		if col == 0:
			if row == 0:
				attribs.text = 'label'
			else:
				attribs.text = self._Nodes[row, 'indentedlabel']
		elif col == 1:
			if row == 0:
				attribs.text = 'path'
			else:
				attribs.text = self._Nodes[row, 'path']
		elif col == 2:
			if row > 0:
				attribs.top = op(self._Nodes[row, 'video'])

	def List_onInitCol(self, col, attribs):
		attribs.textJustify = JustifyType.CENTERLEFT
		if col in [0, 1]:
			attribs.colStretch = True
			attribs.colWidth = None
		elif col == 2:
			attribs.colStretch = False
			attribs.colWidth = 100

	def List_onInitRow(self, row, attribs):
		if row == 0:
			attribs.bgColor = [0.1, 0.1, 0.1, 1]
			attribs.textColor = [0.9, 0.9, 0.9, 1]
			attribs.rowHeight = 20
			attribs.fontItalic = False
		else:
			attribs.rowHeight = 60 if self.comp.par.Inlinepreviews else 20
			attribs.fontItalic = self._Nodes[row, 'nodetype'] != 'data'
		#highlight = False
		#DropMenu._ApplyItemOverrideColors(attribs, highlight=highlight, rollover=False)
		pass

	def List_onInitTable(self, attribs):
		attribs.rowHeight = 20
		attribs.bgColor = DropMenu._ItemRegular['bg']
		attribs.textColor = DropMenu._ItemRegular['text']
		attribs.fontSizeX = float(self._ListSettings['Fontsizex', 1])
		attribs.fontSizeY = float(self._ListSettings['Fontsizey', 1])
		attribs.fontFace = self._ListSettings['Fontface', 1]
		attribs.wordWrap = self._ListSettings['Wordwrap', 1] == '1'
		#attribs.textJustify = JustifyType.CENTERLEFT
		attribs.bottomBorderOutColor = [0.4, 0.4, 0.4, 1]
		self._UpdateRowHighlights()

	def List_onRollover(self, row, col, prevrow, prevcol):
		if self._GetRowAttr(row, 'nodetype') != 'data':
			return
		self._UpdateRowHighlights(rolloverrow=row)

	def List_onSelect(self, startrow, startcol, startcoords, endrow, endcol, endcoords, start, end):
		# self._LogEvent('List_onSelect(%r)' % {'startrow':startrow,'startcol':startcol,'startcoords':startcoords,'endrow':endrow,'endcol':endcol,'endcoords':endcoords,'start':start,'end':end})
		if self._GetRowAttr(endrow, 'nodetype') != 'data':
			return
		self._SelectRow(endrow)
		pass

	def _UpdateRowHighlights(self, rolloverrow=None):
		if rolloverrow == -1:
			rolloverrow = None
		selrowindex = self._SelectedRowIndex
		self.comp.par.Highlightnodeid = self._GetRowId(rolloverrow) or ''
		for row, attribs in enumerate(self._List.rowAttribs):
			if row == 0:
				continue
			isselected = selrowindex == row
			isrollover = rolloverrow is not None and row == rolloverrow
			DropMenu._ApplyItemOverrideColors(
				attribs,
				highlight=isselected,
				rollover=isrollover)
			attribs.fontBold = isselected

class NodeBank(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self._NodeTable = comp.op('./data_nodes')
		self._PopupWindow = comp.op('./selector_popup_window')

	@property
	def _Popup(self):
		if False:
			# trick pycharm
			return NodeSelectorPopup(None)
		return self.comp.op('./selector_popup')

	def ShowPopup(self, targetop, targetpar, nodetype='video'):
		self._Popup.Initialize(targetop, targetpar, nodetype=nodetype)
		self._PopupWindow.par.winopen.pulse()

	def GetNodes(self, datatype=None):
		return [
			{'id': self._NodeTable[i, 'id'].val, 'label': self._NodeTable[i, 'label'].val}
			for i in range(1, self._NodeTable.numRows)
			if not datatype or self._NodeTable[i, datatype] != ''
		]

	def BuildNodeTreeList(self, outdat):
		outdat.clear()
		indat = outdat.inputs[0]
		bankroot = self.comp.par.Rootop.eval()
		cols = ['id', 'path', 'nodetype', 'label', 'indentedlabel', 'video', 'audio', 'texbuf']
		outdat.appendRow(cols)
		nodesbypath = {}
		for i in range(1, indat.numRows):
			path = indat[i, 'path'].val
			parentpath = indat[i, 'parentpath'].val
			parts = parentpath.split('/')
			nodedepth = 1 + len(parts)
			nodesbypath[path] = {
				'id': indat[i, 'id'].val,
				'path': path,
				'indentedlabel': (' ' * nodedepth) + indat[i, 'label'].val,
				'label': indat[i, 'label'].val,
				'video': indat[i, 'video'].val,
				'audio': indat[i, 'audio'].val,
				'texbuf': indat[i, 'texbuf'].val,
				'nodetype': 'data',
				'parentpath': parentpath,
				'depth': nodedepth,
			}
			for depth in range(len(parts)):
				containerpath = '/'.join(parts[:depth + 1])
				if containerpath not in nodesbypath:
					label = _getContainerLabel(containerpath, bankroot)
					nodesbypath[containerpath] = {
						'path': containerpath,
						'nodetype': 'container',
						'parentpath': '/'.join(parts[:depth]),
						'label': label,
						'indentedlabel': (' ' * depth) + label,
						'depth': depth,
					}

		def _outputWithDescendants(node):
			if node['nodetype'] == 'data':
				outdat.appendRow([node[col] for col in cols])
			else:
				cntrpath = node['path']
				outdat.appendRow([])
				row = outdat.numRows - 1
				outdat[row, 'path'] = bankroot.path + '/' + cntrpath
				outdat[row, 'nodetype'] = 'container'
				outdat[row, 'label'] = node['label']
				outdat[row, 'indentedlabel'] = node['indentedlabel']
				childnodes = sorted([child for child in nodesbypath.values() if child['parentpath'] == cntrpath], key=lambda c: c['path'])
				for child in childnodes:
					_outputWithDescendants(child)

		toplevelnodes = sorted([node for node in nodesbypath.values() if not node['parentpath']], key=lambda c: c['path'])
		for node in toplevelnodes:
			_outputWithDescendants(node)

def _getContainerLabel(path, bankroot):
	container = bankroot.op(path)
	if hasattr(container.par, 'Modname'):
		return container.par.Modname.eval()
	else:
		return container.par.opshortcut.eval() or container.name

def GetAppNodeBank():
	app = getattr(op, 'App', None)
	return app and getattr(app, 'DataNodeBank', None)

def GetAppNodes(datatype=None):
	bank = GetAppNodeBank()
	if not bank:
		return []
	return bank.GetNodes(datatype=datatype)
