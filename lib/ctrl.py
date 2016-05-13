print('core/ctrl.py initializing')

import json
try:
	import core_base as base
except ImportError:
	import base

util = base.util
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

def ParseStringList(val):
	if not val:
		return []
	if val.startswith('['):
		return json.loads(val)
	elif ',' in val:
		return [v.strip() for v in val.split(',') if v.strip()]
	else:
		return [val]

def _AddTextPars(page, sourceOp, namePrefix=None, menuSourcePath='', labelPrefix=''):
	def _CopyPar(label, style, sourceName=None, name=None, size=None, fromPattern=None, defaultVal=None):
		util.CopyPar(page, sourceOp, label, style, labelPrefix=labelPrefix, menuSourcePath=menuSourcePath, namePrefix=namePrefix, sourceName=sourceName, name=name, size=size, fromPattern=fromPattern, defaultVal=defaultVal)
	_CopyPar(label='Font', style='Menu')
	# _CopyPar(label='Font File', style='File', sourceName='fontfile')
	_CopyPar(label='Bold', style='Toggle')
	_CopyPar(label='Italic', style='Toggle')
	_CopyPar(label='Auto-Size Font', style='Menu', sourceName='fontautosize', defaultVal='fitiffat')
	_CopyPar(label='Font Size X', style='Float', defaultVal=12)
	_CopyPar(label='Font Size Y', style='Float', defaultVal=12)
	_CopyPar(label='Keep Font Ratio', style='Toggle')
	_CopyPar(label='Horizontal Align', style='Menu', sourceName='alignx', defaultVal='center')
	_CopyPar(label='Vertical Align', style='Menu', sourceName='aligny', defaultVal='center')
	_CopyPar(label='Kerning', style='Float', size=2)
	_CopyPar(label='Position', style='Float', size=2)
	_CopyPar(label='Border Space', style='Float', size=2)
	_CopyPar(label='Word Wrap', style='Toggle')

def _AddBorderPars(page, sourceOp, namePrefix, menuSourcePath='', labelPrefix=''):
	for side in ['Left', 'Right', 'Top', 'Bottom']:
		util.CopyPar(page, sourceOp, label=side + ' Border', style='Menu', defaultVal='bordera', namePrefix=namePrefix, labelPrefix=labelPrefix, menuSourcePath=menuSourcePath)
	for side in ['Left', 'Right', 'Top', 'Bottom']:
		util.CopyPar(page, sourceOp, label=side + ' Border Inside', style='Menu', sourceName=side.lower() + 'borderi', defaultVal='off', namePrefix=namePrefix, labelPrefix=labelPrefix, menuSourcePath=menuSourcePath)

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

	def UNUSED_PushValue(self, val):
		# assert self.IsScripted
		par = self.TargetPar
		if par is None:
			return
		if par.isPulse:
			par.pulse()
		else:
			par.val = val

	def UNUSED_PushDefault(self):
		# assert self.IsScripted
		par = self.TargetPar
		if par is None:
			return
		if not par.isPulse:
			par.val = par.default

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
		_AddTextPars(self.comp.appendCustomPage('Button Text'), sourceOp=self.comp.op('./bg'), namePrefix='Button', menuSourcePath='./bg')
		_AddBorderPars(self.comp.appendCustomPage('Button Border'), sourceOp=self.comp.op('./bg'), namePrefix='Button', menuSourcePath='./bg')
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
		_AddTextPars(self.comp.appendCustomPage('Label'), self.comp.op('./label_and_bg'), namePrefix='Label', menuSourcePath='./label_and_bg')
		self.comp.par.Labelalignx.default = 'left'
		self.comp.par.Labelborderspace1.default = 8
		_AddTextPars(self.comp.appendCustomPage('Value'), self.comp.op('./value_text'), namePrefix='Value', menuSourcePath='./value_text')
		self.comp.par.Valuealignx.default = 'right'
		self.comp.par.Valueborderspace1.default = 8
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

def WarnDeprecatedComponent(comp):
	if comp.par.clone.eval() is None:
		# component is the master
		return
	util.Log('WARNING: deprecated component used: %s (clone of %r)' % (comp.path, comp.par.clone.eval()))
