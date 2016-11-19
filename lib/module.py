print('shell/module.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base
try:
	import common_util as util
except ImportError:
	try:
		import util
	except ImportError:
		import common.lib.util
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
		comp.tags.add('tmod')
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

	def UpdateSolo(self):
		solo = self.comp.par.Solo.eval()
		outnode = self.comp.op(self.Shell.par.Solonode.eval() or self.Shell.par.Solonode.default)
		mainoutsrc = _GetGlobalSourcePar()
		if solo and outnode:
			for m in _GetOtherModules(self.comp.path):
				m.par.Solo = False
			nodeId = outnode.par.Nodeid.eval()
		elif outnode and mainoutsrc == outnode.par.Nodeid:
			nodeId = mainoutsrc.default
		else:
			return
		self._LogEvent('UpdateSolo() - setting solo to %r' % nodeId)
		mainoutsrc.val = nodeId

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

def _GetGlobalSourcePar():
	return op.App.OutputSource

def _GetOtherModules(exceptPath):
	return [m for m in op.App.AllModules if m.path != exceptPath]


class SubModules(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def _ModuleSlotCount(self):
		return 8

	def BuildModuleTable(self, dat):
		dat.clear()
		dat.appendRow(['name', 'label', 'master'])
		for i in range(1, self._ModuleSlotCount + 1):
			spec = self._ParseModuleSpec(i)
			if spec:
				dat.appendRow([spec['name'], spec['label'], spec['master']])

	def _GetSpecPar(self, i):
		return getattr(self.comp.par, 'Modspec%d' % i)

	def _ParseModuleSpec(self, i):
		specjson = self._GetSpecPar(i).eval()
		spec = util.FromJson(specjson)
		if not spec or not spec.get('name') or not spec.get('master'):
			return None
		if not spec.get('label'):
			spec['label'] = spec['name']
		return spec

	@property
	def _HostOP(self):
		return self.comp.par.Hostop.eval() or self.comp

	def OnReplicate(self, allOps, template):
		self._LogBegin('OnReplicate()')
		try:
			for i, submod in enumerate(allOps):
				masterpath = template[i + 1, 'master']
				master = op(masterpath)
				self._LogEvent('OnReplicate() - i: %d submod: %s master path: %r master: %r' % (i+1, submod.path, masterpath, master))
				submod.par.clone = master.path
				submod.par.enablecloningpulse.pulse()
				submod.par.extension1 = master.par.extension1
				submod.par.promoteextension1 = True
				submod.initializeExtensions()
				mname = template[i + 1, 'name'].val
				submod.par.Modname.val = mname
				submod.par.Uilabel.val = mname # TODO: fix this
		finally:
			self._LogEnd()

	def _GetModule(self, i):
		pass

	def _LoadModuleSpec(self, spec, i):
		pass
