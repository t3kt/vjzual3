print('common/ctrl.py initializing')

import json
try:
	import common_base as base
except ImportError:
	import base
try:
	import common_util as util
except ImportError:
	import util

if False:
	try:
		from _stubs import JustifyType
	except ImportError:
		from common.lib._stubs import JustifyType

# util = base.util
setattrs = util.setattrs

def GetTargetPar(ctrl):
	if not ctrl:
		return
	targetOp = ctrl.par.Targetop.eval()
	if not targetOp:
		return
	parName = ctrl.par.Targetpar.eval()
	if not parName:
		return
	return getattr(targetOp.par, parName, None)

ParseStringList = util.ParseStringList

def _AddTextPars(
		page, sourceOp, namePrefix=None, menuSourcePath='', labelPrefix='',
		includeAlignment=True, includeKerning=True, includePosition=True, includeBorderSpace=True,
		includeAutoSize=True, includeBold=True, includeItalic=True):

	def _CopyPar(label, style, sourceName=None, name=None, size=None, fromPattern=None, defaultVal=None):
		util.CopyPar(page, sourceOp, label, style, labelPrefix=labelPrefix, menuSourcePath=menuSourcePath, namePrefix=namePrefix, sourceName=sourceName, name=name, size=size, fromPattern=fromPattern, defaultVal=defaultVal)
	_CopyPar(label='Font', style='Menu')
	# _CopyPar(label='Font File', style='File', sourceName='fontfile')
	if includeBold:
		_CopyPar(label='Bold', style='Toggle')
	if includeItalic:
		_CopyPar(label='Italic', style='Toggle')
	if includeAutoSize:
		_CopyPar(label='Auto-Size Font', style='Menu', sourceName='fontautosize', defaultVal='fitiffat')
	_CopyPar(label='Font Size X', style='Float', defaultVal=12)
	_CopyPar(label='Font Size Y', style='Float', defaultVal=12)
	_CopyPar(label='Keep Font Ratio', style='Toggle')
	if includeAlignment:
		_CopyPar(label='Horizontal Align', style='Menu', sourceName='alignx', defaultVal='center')
		_CopyPar(label='Vertical Align', style='Menu', sourceName='aligny', defaultVal='center')
	if includeKerning:
		_CopyPar(label='Kerning', style='Float', size=2)
	if includePosition:
		_CopyPar(label='Position', style='Float', size=2)
	if includeBorderSpace:
		_CopyPar(label='Border Space', style='Float', size=2)
	_CopyPar(label='Word Wrap', style='Toggle')

def _AddBorderPars(page, sourceOp, namePrefix, menuSourcePath='', labelPrefix=''):
	for side in ['Left', 'Right', 'Top', 'Bottom']:
		util.CopyPar(page, sourceOp, label=side + ' Border', style='Menu', defaultVal='bordera', namePrefix=namePrefix, labelPrefix=labelPrefix, menuSourcePath=menuSourcePath)
	for side in ['Left', 'Right', 'Top', 'Bottom']:
		util.CopyPar(page, sourceOp, label=side + ' Border Inside', style='Menu', sourceName=side.lower() + 'borderi', defaultVal='off', namePrefix=namePrefix, labelPrefix=labelPrefix, menuSourcePath=menuSourcePath)

class Settings(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def ParamTable(self):
		return self.comp.op('./params')

	def FillTable(self, dat):
		util.CopyParPagesToTable(dat, *self.comp.customPages, quotestrings=True)

	@staticmethod
	def FillExportTable(dat, paramtable, exportpath):
		dat.clear()
		dat.appendRow(['path', 'parameter', 'value'])
		for name, val in paramtable.rows():
			dat.appendRow([exportpath, name.val.lower(), val])

class ControlBase(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		# self.PushState()

	def Setup(self):
		self._SetupBaseParams()
		self.PushState()

	def _SetupBaseParams(self):
		page = self.comp.appendCustomPage('Control')
		page.appendOP('Targetop', label='Target OP')
		page.appendStr('Targetpar', label='Target Parameter')
		page.appendStr('Channame', label='Channel Name')
		setattrs(
			page.appendMenu('Bindmode', label='Bind Mode'),
			menuNames=['none', 'script', 'export'],
			menuLabels=['Unbound', 'Scripted', 'Parameter Export'],
			default='script')

	@property
	def TargetPar(self):
		targetOp = self.comp.par.Targetop.eval()
		parName = self.comp.par.Targetpar.eval()
		return getattr(targetOp.par, parName, None) if targetOp and parName else None

	@property
	def IsExported(self):
		return self.comp.par.Bindmode == 'export'

	@property
	def IsScripted(self):
		return self.comp.par.Bindmode == 'script'

	@property
	def IsUnbound(self):
		return self.comp.par.Bindmode == 'none'

	@property
	def DefaultValue(self):
		par = self.TargetPar
		return par.default if par is not None else None

	def ResetValue(self):
		raise NotImplementedError()

	def SetValue(self, val):
		raise NotImplementedError()

	def GetValue(self):
		raise NotImplementedError()

	def LoadValue(self):
		raise NotImplementedError()

	def _UpdateExportStatus(self):
		chop = self.comp.op('val_out')
		chop.export = False
		chop.cook(force=True)
		if self.IsExported:
			chop.export = True
			chop.cook(force=True)

	def PushState(self):
		self._UpdateExportStatus()

class Button(ControlBase):
	def __init__(self, comp):
		super().__init__(comp)

	def Setup(self):
		super().Setup()
		page = self.comp.appendCustomPage('Button')
		page.appendStr('Helptext', label='Help Text')
		page.appendStr('Offhelptext', label='Off Help Text')
		page.appendStr('Buttontext', label='Button Text')
		page.appendStr('Buttonofftext', label='Off Button Text')
		page.appendToggle('Hidetext', label='Hide Text')
		self.LoadValue()

	@property
	def IsPulse(self):
		return self.comp.par.buttontype in ['momentary', 'momentaryup']

	def PushState(self):
		super().PushState()
		if self.IsScripted:
			self.SetValue(self.comp.panel.state)

	def ResetValue(self):
		if self.IsPulse:
			return
		par = self.TargetPar
		if par is None:
			return
		if self.IsScripted:
			par.val = par.default
		else:
			self.comp.click(1 if par.default else 0, force=True)

	def SetValue(self, val):
		par = self.TargetPar
		if self.IsScripted and par is not None:
			if par.isPulse and val:
				par.pulse()
			else:
				par.val = val
		# else:
		self.comp.click(1 if val else 0, force=True)

	def GetValue(self):
		par = self.TargetPar
		if par is not None:
			return par.eval()
		return self.comp.panel.state.val

	def LoadValue(self):
		par = self.TargetPar
		if par is None:
			return
		self.comp.click(1 if par.eval() else 0, force=True)

class Slider(ControlBase):
	def __init__(self, comp):
		super().__init__(comp)

	def Setup(self):
		super().Setup()
		page = self.comp.appendCustomPage('Slider')
		page.appendStr('Helptext', label='Help Text')
		page.appendStr('Label', label='Label')
		page.appendFloat('Normrange', label='Normalized Range', size=2)
		self.comp.par.Normrange2.default = 1
		page.appendToggle('Hidelabel', label='Hide Label')
		page.appendToggle('Hidevalue', label='Hide Value')
		setattrs(page.appendInt('Decimals', label='Decimals'), min=0, clampMin=True, normMax=4, default=2)
		page.appendPulse('Loadsettings', label='Load Settings')
		self.LoadValue()

	def PushState(self):
		super().PushState()
		if self.IsScripted:
			self.SetNormalizedValue(self.comp.panel.u)

	def SetNormalizedValue(self, normval):
		par = self.TargetPar
		if par is None:
			self.comp.click(normval, force=True)
		else:
			par.normVal = normval

	def _NormalizeValue(self, val):
		return util.interp(val, self._NormRange, [0, 1])

	def _DeormalizeValue(self, normval):
		return util.interp(normval, [0, 1], self._NormRange)

	@property
	def _NormRange(self):
		return [self.comp.par.Normrange1.eval(), self.comp.par.Normrange2.eval()]

	def SetValue(self, val):
		# self._LogEvent('SetValue(%r)' % val)
		# par = self.TargetPar
		# if self.IsScripted and par is not None:
		# 	par.val = val
		# else:
		normval = self._NormalizeValue(val)
		# self._LogEvent('SetValue(%r) using click with norm val %r' % (val, normval))
		self.comp.click(normval, force=True)

	def PushNormalizedValue(self, normval):
		# self._LogEvent('PushNormalizedValue(normval=%r)' % normval)
		par = self.TargetPar
		if self.IsScripted and par is not None:
			par.normVal = normval

	def GetValue(self):
		par = self.TargetPar
		if par is not None:
			return par.eval()
		return self.comp.op('val_out')[0].eval()

	def ResetValue(self):
		par = self.TargetPar
		if par is None:
			return
		if self.IsScripted:
			par.val = par.default
		else:
			self.comp.click(self._NormalizeValue(par.default), force=True)

	def LoadValue(self):
		par = self.TargetPar
		if par is None:
			return
		self.comp.click(self._NormalizeValue(par.eval()), force=True)

	def LoadSettings(self):
		par = self.TargetPar
		if par is None:
			return
		if par.isToggle:
			self.comp.par.Normrange1 = 0
			self.comp.par.Normrange2 = 1
			self.comp.par.Decimals = 0
		if par.isNumber:
			self.comp.par.Normrange1 = par.normMin
			self.comp.par.Normrange2 = par.normMax
		if par.isInt:
			self.comp.par.Decimals = 0

class DropMenu(ControlBase):
	def __init__(self, comp):
		super().__init__(comp)

	_DisplayModeNames = ['name', 'label', 'both']
	_DisplayModeLabels = ['Value Name', 'Value Label', 'Value Name and Label']

	#TODO: do something less awkward for color settings
	_ItemRegular = {
		'bg': [0.23, 0.23, 0.23, 1],
		'text': [0.73, 0.73, 0.73, 1],
	}
	_ItemHighlight = {
		'bg': [0.43, 0.43, 0.43, 1],
		'text': [0.9, 0.9, 0.9, 1],
	}
	_ItemRegularRollover = {
		'bg': [0.4, 0.4, 0.4, 1],
		'text': [0.73, 0.73, 0.73, 1],
	}
	_ItemHighlightRollover = {
		'bg': [0.6, 0.6, 0.6, 1],
		'text': [0.9, 0.9, 0.9, 1],
	}

	@staticmethod
	def _ApplyItemOverrideColors(attribs, highlight, rollover):
		if highlight:
			colors = DropMenu._ItemHighlightRollover if rollover else DropMenu._ItemHighlight
		else:
			colors = DropMenu._ItemRegularRollover if rollover else None
		attribs.bgColor = colors['bg'] if colors else None
		attribs.textColor = colors['text'] if colors else None

	def Setup(self):
		super().Setup()
		page = self.comp.appendCustomPage('Drop Menu')
		page.appendStr('Helptext', label='Help Text')
		page.appendPulse('Loadsettings', label='Load Settings')
		page.appendToggle('Hidetext', label='Hide Text')
		page.appendToggle('Hidearrow', label='Hide Arrow')
		page.appendStr('Menunames', label='Menu Names')
		page.appendStr('Menulabels', label='Menu Labels')
		page.appendDAT('Menudat', label='Menu DAT')
		setattrs(page.appendMenu('Buttondisplay', label='Button Display'), menuNames=DropMenu._DisplayModeNames, menuLabels=DropMenu._DisplayModeLabels, default='label')
		setattrs(page.appendInt('Currentindex', label='(INTERNAL) Current Index'), normMax=10)

		page = self.comp.appendCustomPage('Popup')
		setattrs(page.appendInt('Popupwidth', label='Popup Width'), min=1, normMin=5, clampMin=True, normMax=300, default=150)
		setattrs(page.appendInt('Popupmaxheight', label='Popup Max Height'), min=0, normMin=5, clampMin=True, normMax=500, default=0)
		setattrs(page.appendInt('Popupitemheight', label='Item Height'), min=1, normMin=5, clampMin=True, normMax=60, default=20)
		setattrs(page.appendToggle('Popuphscrollbar', label='Horizontal Scroll Bar'), default=False)
		setattrs(page.appendToggle('Popupvscrollbar', label='Vertical Scroll Bar'), default=True)
		setattrs(page.appendMenu('Popupitemdisplay', label='Popup Item Display'), menuNames=DropMenu._DisplayModeNames, menuLabels=DropMenu._DisplayModeLabels, default='label')

		self.UpdateRowHighlights()

	@property
	def CurrentState(self):
		return self.comp.op('current')

	@property
	def ButtonText(self):
		current = self.CurrentState
		mode = self.comp.par.Buttondisplay.eval()
		if current.numRows == 0 or current.numCols == 0:
			return ''
		if mode == 'name':
			return current[0, 0].val
		elif mode == 'label':
			return current[0, 1].val
		elif mode == 'both':
			return '%s (%s)' % (current[0, 1], current[0, 0])

	def SetValue(self, val):
		# self._LogEvent('SetValue(%r)' % val)
		par = self.TargetPar
		if self.IsScripted and par is not None:
			par.val = val
		index = self._NameToIndex(val)
		self.comp.par.Currentindex = index if index is not None else 0
		self.UpdateRowHighlights()

	def SetValueIndex(self, index):
		# self._LogEvent('SetValueIndex(%r)' % index)
		par = self.TargetPar
		if self.IsScripted and par is not None:
			if par.isString:
				par.val = self._IndexToName(index)
			elif par.isMenu:
				par.menuIndex = index
			else:
				par.val = index
		self.comp.par.Currentindex = index
		self.UpdateRowHighlights()

	def GetValue(self):
		return self.CurrentState[0, 0].val

	def GetValueIndex(self):
		return self.comp.par.Currentindex.eval()

	def ResetValue(self):
		par = self.TargetPar
		if par is None:
			return
		self.SetValue(par.default)

	def LoadValue(self):
		par = self.TargetPar
		if par is None:
			return
		self.SetValue(par.eval())

	def PushValue(self):
		par = self.TargetPar
		if par is None:
			return
		if self.IsScripted:
			par.val = self.GetValue()
		elif self.IsExported:
			# get around annoying export bug
			par.owner.cook()

	def _NameToIndex(self, name):
		cell = self.MenuOptions[name, 0]
		return cell.row if cell is not None else None

	def _IndexToName(self, index):
		opts = self.MenuOptions
		return opts[index, 0].val if index < opts.numRows else None

	def FillOptionsTable(self, dat):
		dat.clear()
		dat.appendCol(ParseStringList(self.comp.par.Menunames.eval()))
		dat.appendCol(ParseStringList(self.comp.par.Menulabels.eval()))

	@property
	def MenuOptions(self):
		return self.comp.op('menu_options')

	@property
	def OptionsList(self):
		return self.comp.op('options_list')

	@property
	def PopupSettings(self):
		return self.comp.op('popup_settings')

	def LoadSettings(self):
		par = self.TargetPar
		if par is None or not par.isMenu:
			return
		self.comp.par.Menunames = json.dumps(par.menuNames)
		self.comp.par.Menulabels = json.dumps(par.menuLabels)
		self.OptionsList.par.reset.pulse()

	def List_onInitCell(self, row, col, attribs):
		opts = self.MenuOptions
		displaymode = self.comp.par.Popupitemdisplay.eval()
		if displaymode == 'label' or (displaymode == 'both' and col == 1):
			attribs.text = opts[row, 1]
		else:
			attribs.text = opts[row, 0]

	def List_onInitCol(self, col, attribs):
		attribs.colStretch = True
		displaymode = self.comp.par.Popupitemdisplay.eval()
		if displaymode != 'both':
			attribs.textJustify = JustifyType.CENTER
			attribs.textOffsetX = 0
		elif col == 0:
			attribs.textJustify = JustifyType.CENTERRIGHT
			attribs.textOffsetX = -4
		else:
			attribs.textJustify = JustifyType.CENTERLEFT
			attribs.textOffsetX = 4

	def List_onInitRow(self, row, attribs):
		opts = self.MenuOptions
		valname = opts[row, 0].val
		vallabel = opts[row, 1].val
		if valname == vallabel:
			attribs.help = valname
		else:
			attribs.help = '%s (%s)' % (vallabel, valname)
		highlight = valname == self.GetValue()
		DropMenu._ApplyItemOverrideColors(attribs, highlight=highlight, rollover=False)
		attribs.fontBold = highlight

	def List_onInitTable(self, attribs):
		settings = self.PopupSettings
		attribs.rowHeight = self.comp.par.Popupitemheight
		attribs.bgColor = DropMenu._ItemRegular['bg']
		attribs.textColor = DropMenu._ItemRegular['text']
		attribs.fontSizeX = float(settings['Fontsizex', 1])
		attribs.fontSizeY = float(settings['Fontsizey', 1]) if bool(settings['Keepfontratio', 1]) else float(settings['Fontsizex', 1])
		attribs.fontFace = settings['Font', 1]
		attribs.wordWrap = bool(settings['Wordwrap', 1])

	def List_onRollover(self, listcomp, row, col, prevrow, prevcol):
		self.UpdateRowHighlights(row)

	def List_onSelect(self, listcomp, startrow, startcol, startcoords, endrow, endcol, endcoords, start, end):
		# self._LogEvent('List_onSelect(start: %r, end: %r, startrow: %r, endrow: %r)' % (start, end, startrow, endrow))
		if end:
			self.SetValueIndex(endrow)
			self.SetPopupVisible(False)

	def SetPopupVisible(self, visible):
		window = self.comp.op('options_window')
		if visible:
			window.par.winopen.pulse()
		else:
			window.par.winclose.pulse()

	def UpdateRowHighlights(self, rolloverrow=None):
		if rolloverrow == -1:
			rolloverrow = None
		listcomp = self.OptionsList
		valindex = self.GetValueIndex()
		# self._LogEvent('UpdateRowHighlights(rolloverRow=%r) .. valindex: %r' % (rolloverrow, valindex))
		for row, attribs in enumerate(listcomp.rowAttribs):
			isselected = valindex == row
			isrollover = rolloverrow is not None and row == rolloverrow
			# self._LogEvent('UpdateRowHighlights() row=%r, val=%r, isselected=%r, isrollover=%r' % (row, self.MenuOptions[row, 0].val, isselected, isrollover))
			DropMenu._ApplyItemOverrideColors(
				attribs,
				highlight=isselected,
				rollover=isrollover)
			attribs.fontBold = isselected

	@property
	def ListHeight(self):
		maxheight = self.comp.par.Popupmaxheight.eval()
		itemheight = self.comp.par.Popupitemheight.eval()
		numitems = self.MenuOptions.numRows
		height = itemheight * numitems
		return min(height, maxheight) if maxheight > 0 else height

class TextField(ControlBase):
	def __init__(self, comp):
		super().__init__(comp)

	def Setup(self):
		super().Setup()
		page = self.comp.appendCustomPage('Field')
		page.appendStr('Helptext', label='Help Text')
		page.appendToggle('Hidelabel', label='Hide Label')
		util.CopyPar(page, self.comp.op('field'), 'Field Type', 'Menu')
		page.appendStr('Label')
		setattrs(page.appendInt('Labelwidth', label='Label Width'), min=0, normMin=5, normMax=200, default=60)
		_AddTextPars(
			self.comp.appendCustomPage('Label Text'),
			namePrefix='Label',
			sourceOp=self.comp.op('./label/bg'),
			menuSourcePath='./label/bg')
		_AddTextPars(
			self.comp.appendCustomPage('Field Text'),
			namePrefix='Field',
			sourceOp=self.comp.op('./field/text'),
			menuSourcePath='./field/text')
		self.comp.par.Fieldalignx.default = 'left'
		self.comp.par.Fieldposition1.default = 2
		self.comp.par.Fieldborderspace1.default = 2
		_AddBorderPars(
			self.comp.appendCustomPage('Border'),
			namePrefix='Label',
			labelPrefix='Label ',
			sourceOp=self.comp.op('./label/bg'),
			menuSourcePath='./label/bg')
		_AddBorderPars(
			self.comp.appendCustomPage('Border'),
			namePrefix='Field',
			labelPrefix='Field ',
			sourceOp=self.comp.op('./field/text'),
			menuSourcePath='./field/text')
		self.LoadValue()

	@property
	def FieldType(self):
		return self.comp.par.Fieldtype.eval()

	@property
	def IsString(self):
		return self.FieldType == 'string'

	@property
	def IsNumber(self):
		return self.FieldType in ['float', 'integer']

	def _GetValueCell(self):
		return self.comp.op('./field/string')[0, 0]

	def GetValue(self):
		cell = self._GetValueCell()
		if self.IsNumber:
			return util.ParseFloat(cell.val)
		return cell.val

	def PushState(self):
		super().PushState()
		if self.IsScripted:
			self.SetValue(self.GetValue())
		elif self.IsExported:
			par = self.TargetPar
			if par is not None:
				par.owner.cook()

	def ResetValue(self):
		defaultVal = self.DefaultValue
		if defaultVal is None:
			return
		self.SetValue(defaultVal)

	def SetValue(self, val):
		par = self.TargetPar
		if self.IsNumber:
			val = util.ParseFloat(val, defaultVal=par.default if par is not None else 0)
		if self.IsScripted and par is not None:
			if par.isMenu and self.IsNumber:
				par.menuIndex = val
			else:
				par.val = val
		self._GetValueCell().val = val

	def LoadValue(self):
		par = self.TargetPar
		if par is None:
			return
		self.SetValue(par.eval())

	def _UpdateExportStatus(self):
		export = self.comp.op('val_out_export')
		if self.IsExported:
			export.cook(force=True)
			par = self.TargetPar
			if par is not None:
				par.owner.cook()

def WarnDeprecatedComponent(comp):
	if comp.par.clone.eval() is None:
		# component is the master
		return
	util.Log('WARNING: deprecated component used: %s (clone of %r)' % (comp.path, comp.par.clone.eval()))
