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
		nodes = self._Nodes
		if not row or row == -1 or row >= nodes.numRows:
			return None
		return nodes[row, 'id'].val

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
			attribs.text = self._Nodes[row, 'label']
		elif col == 1:
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
		else:
			attribs.rowHeight = 60 if self.comp.par.Inlinepreviews else 20
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
		self._UpdateRowHighlights(rolloverrow=row)

	def List_onSelect(self, startrow, startcol, startcoords, endrow, endcol, endcoords, start, end):
		# self._LogEvent('List_onSelect(%r)' % {'startrow':startrow,'startcol':startcol,'startcoords':startcoords,'endrow':endrow,'endcol':endcol,'endcoords':endcoords,'start':start,'end':end})
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
