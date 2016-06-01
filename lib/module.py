print('shell/module.py initializing')

try:
	import common_base as base
except ImportError:
	import base
try:
	import common_util as util
except ImportError:
	import util
try:
	import shell_mapping as mapping
except ImportError:
	import mapping

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

class Module(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def Shell(self):
		return self.comp.op('./shell')

	@property
	def BodyPanel(self):
		return self.comp.op('./body_panel')

	@property
	def ControlPanel(self):
		return self.comp.op('./controls_panel')

	@property
	def _HeaderHeight(self):
		return 20 if self.comp.par.Collapsed else 40

	@property
	def _BodyHeight(self):
		if self.comp.par.Collapsed:
			return 0
		panel = self.BodyPanel
		return panel.par.h if panel else 20

	def UpdateHeight(self):
		self._UpdateControlPanelHeight()
		self._UpdateBodyPanelHeight()
		h = self._HeaderHeight
		h += self._BodyHeight
		self.comp.par.h = h

	def _UpdateBodyPanelHeight(self):
		panel = self.BodyPanel
		if panel:
			panel.par.h = util.GetVisibleChildCOMPsHeight(panel)

	def _UpdateControlPanelHeight(self):
		panel = self.ControlPanel
		if panel:
			panel.par.h = util.GetVisibleChildCOMPsHeight(panel)

	@property
	def ModParams(self):
		parnames = util.ParseStringList(self.Shell.par.Modparams.eval())
		pagenames = util.ParseStringList(self.Shell.par.Modparampages.eval())
		pars = self.comp.pars(*parnames)
		for page in self.comp.customPages:
			if page.name in pagenames:
				pars += page.pars
		return pars

	def _GetModParamsDict(self):
		return {
			par.name.lower(): par.eval()
			for par in self.ModParams
		}

	def _LoadModParamsDict(self, params):
		self._LogEvent('_LoadModParamsDict(%r)' % params)
		if not params:
			return
		for name, val in params.items():
			par = self.comp.pars(name.capitalize())[0]
			if par is None:
				self._LogEvent('_LoadModParamsDict() - cannot find parameter %r' % name)
			elif par.mode != ParMode.CONSTANT:
				self._LogEvent('_LoadModParamsDict() - cannot set parameter %r which has mode %r' % (name, par.mode))
			else:
				par.val = val

	def GetStateDict(self):
		state = {
			'modname': self.comp.par.Modname.eval(),
			'label': self.comp.par.Uilabel.eval(),
			'path': self.comp.path,
			'bypass': self.comp.par.Bypass.eval(),
			'solo': self.comp.par.Solo.eval(),
			'uistate': {
				'collapsed': self.comp.par.Collapsed.eval(),
				'uimode': self.comp.par.Uimode.eval(),
				'showadvanced': self.comp.par.Showadvanced.eval(),
				'showviewers': self.comp.par.Showviewers.eval(),
			},
			'params': self._GetModParamsDict(),
		}
		ctrlmappings = mapping.GetMappingsFromHost(self.comp)
		ctrlmappings = {
			name: opts for name, opts in ctrlmappings.items() if opts.get('ctrl')
		}
		if ctrlmappings:
			state['mappings'] = ctrlmappings
		return state

	def LoadStateDict(self, state):
		self._LogEvent('LoadStateDict(%r)' % state)
		if not state:
			return
		self.comp.par.Bypass = state.get('bypass', state.comp.par.Bypass)
		self._LoadParVals(
			state,
			[
				'Bypass',
				'Solo'
			])
		self._LoadParVal('Solo', state)
		raise NotImplementedError()

	def _LoadParVal(self, state, parname, key=None):
		if not key:
			key = parname.lower()
		if key not in state:
			return
		par = self.comp.pars(parname)[0]
		if par is None:
			self._LogEvent('_LoadParVal(parname=%r, key=%r) - parameter not found' % (parname, key))
		if par.mode != ParMode.CONSTANT:
			self._LogEvent('_LoadParVal(parname=%r, key=%r) - cannot set parameter because it has mode %r' % (parname, key, par.mode))
		val = state.get(key)
		if val is not None:
			par.val = val

	def _LoadParVals(self, state, parnames=None, getkey=None):
		if parnames is None:
			parnames = state.keys()
		for parname in parnames:
			self._LoadParVal(state, parname, key=getkey(parname) if getkey else None)

class ParTypeHandler:
	def __init__(self, floatdecimals=4):
		self.floatdecimals = floatdecimals

	def PrepValueForPar(self, par, value):
		if par.isToggle:
			return self._CoerceBool(value)
		return value

	def CleanValueFromPar(self, par):
		val = par.eval()
		if isinstance(val, float):
			return self._CleanFloat(val)
		return val

	def _CleanFloat(self, value):
		return round(value, self.floatdecimals)

	def _CoerceBool(self, value):
		if isinstance(value, bool):
			return value
		if isinstance(value, (int, float)):
			return bool(value)
		return value in ('1', 'true', 'TRUE', 't', 'T')

_DefaultParTypeHandler = ParTypeHandler()

