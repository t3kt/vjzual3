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

def InitializeModule(comp):
	if not comp:
		return
	util.Log('InitializeModule(%r)' % comp)
	comp.par.parentshortcut = 'tmod'
	if not comp.par.extension1:
		comp.par.extension1 = 'mod.shell_module.Module(me)'
		comp.par.promoteextension1 = True
		comp.initializeExtensions()

class Module(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.parAccessor = ParAccessor(comp)

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

	def _GetModParamTuplets(self):
		tupletnames = util.ParseStringList(self.Shell.par.Modparamtuples.eval())
		pagenames = util.ParseStringList(self.Shell.par.Modparampages.eval())
		tuplets = []
		for page in self.comp.customPages:
			if page.name in pagenames:
				tuplets += page.parTuplets
		for t in self.comp.customTuplets:
			if t[0].tupletName in tupletnames:
				tuplets.append(t)
		return _ExcludePulsePars(tuplets)

	def _GetModParamsDict(self):
		return self.parAccessor.GetParTupletVals(self._GetModParamTuplets())

	def _LoadModParamsDict(self, params):
		self._LogEvent('_LoadModParamsDict(%r)' % params)
		if not params:
			return
		self.parAccessor.SetParTupletVals(self._GetModParamTuplets(), params)

	def GetStateDict(self):
		state = util.MergeDicts(
			self.parAccessor.GetParTupletVals(self.parAccessor.GetCustomPage('Module').parTuplets),
			{
				'path': self.comp.path,
				'params': self._GetModParamsDict(),
			},
		)
		ctrlmappings = mapping.GetMappingsFromHost(self.comp)
		ctrlmappings = {
			parname: opts for parname, opts in ctrlmappings.items() if opts.get('ctrl')
		}
		if ctrlmappings:
			state['mappings'] = ctrlmappings
		return state

	def LoadStateDict(self, state):
		self._LogEvent('LoadStateDict(%r)' % state)
		if not state:
			return
		self.parAccessor.SetParTupletVals(self.parAccessor.GetCustomPage('Module').parTuplets, state)
		self.parAccessor.SetParTupletVals(self._GetModParamTuplets(), state.get('params', {}))

class ParAccessor(base.Extension):
	def __init__(self, comp, getkey=None, floatdecimals=4):
		super().__init__(comp)
		self.getkey = getkey
		self.floatdecimals = floatdecimals

	def SetParVal(self, par, value):
		if par.isToggle:
			value = self._CoerceBool(value)
		if par.mode != ParMode.CONSTANT:
			self._LogEvent('SetParVal() - cannot set value of par %r which has mode %r' % (par, par.mode))
		elif par.isPulse:
			self._LogEvent('SetParVal() - cannot set value of pulse par %r' % par)
		else:
			par.val = value

	def GetParVal(self, par):
		val = par.eval()
		if isinstance(val, float):
			return self._CleanFloat(val)
		return val

	def _CleanFloat(self, value):
		return round(value, self.floatdecimals) if self.floatdecimals else value

	def _CoerceBool(self, value):
		if isinstance(value, bool):
			return value
		if isinstance(value, (int, float)):
			return bool(value)
		return value in ('1', 'true', 'TRUE', 't', 'T')

	def _GetKey(self, parname):
		return self.getkey(parname) if self.getkey else parname.lower()

	def _GetPars(self, parnames):
		if isinstance(parnames, str):
			parnames = [parnames]
		if not parnames:
			return []
		pars = []
		for parname in parnames:
			if isinstance(parname, str):
				pars += self.comp.pars(parname)
			else:
				pars += [parname]
		return pars

	def GetParTupletVals(self, tuplets):
		if hasattr(tuplets, 'parTuplets'):
			tuplets = tuplets.parTuplets
		return {
			self._GetKey(t[0].tupletName):
				[self.GetParVal(p) for p in t] if len(t) > 1 else self.GetParVal(t[0])
			for t in tuplets
		}

	def GetParVals(self, parnames):
		return {
			self._GetKey(p.name): self.GetParVal(p)
			for p in self._GetPars(parnames)
		}

	def SetParTupletVals(self, tuplets, state, usedefaults=False):
		if hasattr(tuplets, 'parTuplets'):
			tuplets = tuplets.parTuplets
		for t in tuplets:
			key = self._GetKey(t[0].tupletName)
			vals = state.get(key)
			if vals is None or vals == '' or vals == []:
				if usedefaults:
					vals = [p.default for p in t]
				else:
					continue
			if not isinstance(vals, (list, tuple)):
				vals = [vals]
			for i, p in enumerate(t):
				val = vals[i if i < len(vals) else 0]
				self.SetParVal(p, val)

	def GetCustomPage(self, pagename):
		for page in self.comp.customPages:
			if page.name == pagename:
				return page

def _IsNotPulse(t):
	if isinstance(t, tuple):
		t = t[0]
	return getattr(t, 'isPulse', False)

def _ExcludePulsePars(pars):
	return filter(_IsNotPulse, pars)
