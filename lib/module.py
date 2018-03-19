print('shell/module.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base
try:
	import common_util as util
except ImportError:
	try:
		import util
	except ImportError:
		import common.lib.util as util

if False:
		from _stubs import *

def InitializeModule(comp):
	if not comp:
		return
	util.Log('InitializeModule(%r)' % comp)
	comp.par.parentshortcut = 'tmod'
	if not comp.par.extension1:
		comp.par.extension1 = 'mod.shell_module.Module(me)'
		comp.par.promoteextension1 = True
		comp.initializeExtensions()

class ModuleBase(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		comp.tags.add('tmod')
		self.Shell = comp.op('./shell')
		self.BodyPanel = comp.op('./body_panel')
		self.ControlPanel = comp.op('./controls_panel')

	@property
	def IsModuleStub(self): return True

	@property
	def HasApp(self): return _GetApp() is not None

	@property
	def _SubModules(self):
		return self.comp.findChildren(depth=1, tags=['tmod'])

	def ResetState(self):
		if hasattr(self.comp.par, 'Resetstatescript'):
			script = self.comp.par.Resetstatescript.eval()
			if script:
				script.run()
		for child in self._SubModules:
			child.ResetState()

def _LoadSchemaMod():
	try:
		return mod.shell_schema
	except ImportError:
		return None

class Module(ModuleBase):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def IsModuleStub(self): return False

	def ResetState(self):
		self._LogBegin('ResetState()')
		try:
			super().ResetState()
		finally:
			self._LogEnd('ResetState()')

	@property
	def SubModuleOpNames(self):
		return [m.name for m in self._SubModules]

	@property
	def SelectorOpNames(self):
		return [s.name for s in self.comp.findChildren(depth=1, parName='clone', parValue='*_selector')]

	def UpdateHeight(self):
		ctrlpanel = self.ControlPanel
		if ctrlpanel:
			ctrlpanel.par.h = util.GetVisibleChildCOMPsHeight(ctrlpanel)
		bodypanel = self.BodyPanel
		try:
			headerheight = 20 if self.comp.par.Collapsed else 40
		except Exception as e:
			print('ERROR in UpdateHeight: comp:', self.comp)
			print('-- pars: ', [p.name for p in self.comp.pars('[A-Z]*')])
			raise e
		if self.Shell.par.Autoheight:
			if bodypanel:
				bodypanel.par.h = util.GetVisibleChildCOMPsHeight(bodypanel)
			h = headerheight
			if not self.comp.par.Collapsed:
				h += bodypanel.par.h if bodypanel else 20
			self.comp.par.h = h
		else:
			if bodypanel:
				bodypanel.par.h = self.comp.par.h - headerheight

	@property
	def ExposedModParamNames(self):
		names = []
		shell_schema = _LoadSchemaMod()
		if not shell_schema:
			overrides = None
		else:
			overrides = shell_schema.GetModuleParamMetadatOverrides(self.comp)
		for t in self.GetModParamTuplets():
			if overrides and overrides[t[0].tupletName, 'expose'] == '0':
				continue
			for p in t:
				names.append(p.name)
		return names

	def GetModParamTuplets(self):
		return _GetModParamTuplets(self.comp)

	def UpdateSolo(self):
		solo = self.comp.par.Solo.eval()
		outnode = self.comp.op(self.Shell.par.Solonode.eval() or self.Shell.par.Solonode.default)
		mainoutsrc = _GetGlobalSourcePar()
		if mainoutsrc is None:
			return
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

	def _GetParameterFlag(self, parname, key, defaultval=False):
		shell_schema = _LoadSchemaMod()
		if not shell_schema:
			return defaultval
		return shell_schema.GetFlagForParameter(self.comp, parname, key, defaultval=defaultval)

	def _GetParamTupletsWithFlag(self, flag, defaultval=False):
		def _predicate(tuplet):
			return self._GetParameterFlag(tuplet[0].tupletName, flag, defaultval)
		return filter(_predicate, self.comp.customTuplets)

	def GetParamsWithFlag(self, flag, defaultval=False):
		return [p for t in self._GetParamTupletsWithFlag(flag, defaultval) for p in t]

_ParamMetaKeys = [
	'store',
	'source',
	'advanced',
	'expose',
	'help',
	'offhelp',
	'btntext',
	'btnofftext',
	'mappable',
	'filterable',
	'sequenceable',
]

def _GetModParamTuplets(comp):
	return [
		t for page in comp.customPages
		if page.name != 'Module'
		for t in page.parTuplets
	]

def _ExtractVal(x):
	if x is None:
		return None
	if hasattr(x, 'val'):
		return x.val
	return x

def _CoerceBool(value):
	if isinstance(value, bool):
		return value
	if isinstance(value, (int, float)):
		return bool(value)
	return value in ('1', 'true', 'TRUE', 't', 'T')

def _GetGlobalSourcePar():
	appOp = _GetApp()
	if appOp is None:
		return None
	return getattr(appOp, 'OutputSource', None)

def _GetOtherModules(exceptPath):
	appOp = _GetApp()
	if appOp is None:
		return []
	return [m for m in appOp.AllModules if m.path != exceptPath]

def _GetApp():
	return getattr(op, 'App', None)

class SubModules(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self._opNamePrefix = "mod__"
		self._slotCount = 8

	def BuildModuleTable(self, dat):
		dat.clear()
		dat.appendRow(['name', 'label', 'master', 'oppath'])
		for i in range(1, self._slotCount + 1):
			spec = self._ParseModuleSpec(i)
			if spec:
				modname = spec['name']
				dat.appendRow([modname, spec['label'], spec['master'], self._GetSubModPath(i)])

	def _GetSubModPath(self, modname):
		return '%s/%s%s' % (self.comp.path, self._opNamePrefix, modname)

	def _GetSubModule(self, modname):
		return self.comp.op(self._GetSubModPath(modname))

	@property
	def _ModuleTable(self):
		return self.comp.op('./module_table')

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

	# @property
	# def _HostOP(self):
	# 	return self.comp.par.Hostop.eval()

	def _CreateModule(self, modname, label, masterpath):
		self._LogBegin('_CreateModule(name: %r, label: %r, master: %r' % (modname, label, masterpath))
		try:
			master = self.comp.op(masterpath)
			if not master:
				raise Exception('No master for module %r' % modname)
			opname = self._opNamePrefix + modname
			submod = self.comp.create(type(master), opname)
			submod.par.clone = master.path
			submod.par.enablecloningpulse.pulse()
			submod.par.extension1 = master.par.extension1
			submod.par.promoteextension1 = True
			submod.initializeExtensions()
			submod.python = False
			submod.par.Modname.val = "`pars('../Modnameprefix')`/" + modname
			submod.par.Uilabel.val = "`pars('../Uilabelprefix')`/" + label
			return submod
		finally:
			self._LogEnd()

	def _ClearModules(self):
		self._LogBegin('_ClearModules()')
		try:
			for submod in self.comp.findChildren(depth=1, tags=['tmod']):
				self._LogEvent('_ClearModules() - destroying %r' % submod)
				submod.destroy()
		finally:
			self._LogEnd()

	def _CreateModules(self):
		self._LogBegin('_CreateModules()')
		try:
			modules = self._ModuleTable
			for i in range(1, modules.numRows):
				self._CreateModule(
					modname=modules[i, 'name'].val,
					label=modules[i, 'label'].val,
					masterpath=modules[i, 'master'].val
				)
		finally:
			self._LogEnd()

	@property
	def _ModulesInOrder(self):
		orderjson = self.comp.par.Modorder.eval()
		orderedkeys = util.FromJson(orderjson, [])
		moduletbl = self._ModuleTable
		othernames = [c.val for c in self._ModuleTable.col('name')[1:]]
		for key in orderedkeys:
			namecell = moduletbl[key, 'name']
			if not namecell:
				continue
			mpath = moduletbl[namecell.row, 'oppath']
			m = self.comp.op(mpath)
			if m:
				yield m
				othernames.remove(namecell.val)
		for mname in othernames:
			mpath = moduletbl[mname, 'oppath']
			m = self.comp.op(mpath)
			if m:
				yield m

	@property
	def _DryVideo(self):
		return self.comp.op('./dry_video')

	@staticmethod
	def _GetFirstVideoInConnector(submod):
		for conn in submod.inputConnectors:
			if conn.inOP and conn.inOP.isTOP:
				return conn

	@staticmethod
	def _GetFirstVideoOutConnector(submod):
		for conn in submod.outputConnectors:
			if conn.outOP and conn.outOP.isTOP:
				return conn

	def _ConnectModules(self):
		self._LogBegin('_ConnectModules()')
		try:
			modules = list(self._ModulesInOrder)
			previousvideo = self._DryVideo
			prevout = previousvideo.outputConnectors[0] if previousvideo else None
			for submod in modules:
				submodin = self._GetFirstVideoInConnector(submod)
				submodout = self._GetFirstVideoOutConnector(submod)
				if submodin:
					submodin.disconnect()
					if prevout:
						submodin.conect(prevout)
				prevout = submodout  # redundant: or None
		finally:
			self._LogEnd()

	def RebuildModules(self):
		self._LogBegin('RebuildModules()')
		try:
			self._ClearModules()
			self._CreateModules()
			self._ConnectModules()
		finally:
			self._LogEnd()

class MacroCore(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.Macros = [
			MacroCore.Macro(comp, i)
			for i in range(1, 9)
		]
		self.Targets = MacroCore.TargetOptions(comp)

	@property
	def _Exports(self):
		if self.comp.par.Bypass:
			return []
		results = []
		for i in range(1, 9):
			active = getattr(self.comp.par, 'Mapactive%d' % i).eval()
			source = getattr(self.comp.par, 'Mapsrc%d' % i)
			target = getattr(self.comp.par, 'Maptarget%d' % i).eval()
			param = getattr(self.comp.par, 'Mapparam%d' % i).eval()
			if active and source and target and param:
				results.append([source, '%s:%s' % (target, param)])
		return results

	@property
	def ExportSelectChans(self):
		return [e[0] for e in self._Exports]

	@property
	def ExportTargets(self):
		return [e[1] for e in self._Exports]

	class Macro:
		def __init__(self, m, i):
			self.Label = getattr(m.par, 'Label%d' % i)
			self.Value = getattr(m.par, 'Value%d' % i)
			self.Default = getattr(m.par, 'Default%d' % i)
			self.TargetParams = MacroCore.ParamOptions(m, i)

	class TargetOptions:
		def __init__(self, m):
			self.m = m

		@property
		def _Root(self): return self.m.par.Scoperoot.eval() or _GetApp()

		@property
		def _Targets(self):
			root = self._Root
			if root is None:
				return []
			targets = []
			if 'tmod' in root.tags:
				targets.append(root)
			return targets + root.findChildren(tags=['tmod'])

		@property
		def menuNames(self): return [t.path for t in self._Targets]

		@property
		def menuLabels(self): return [t.par.Modname for t in self._Targets]

	class ParamOptions:
		def __init__(self, m, i):
			self.m = m
			self.target = getattr(m.par, 'Maptarget%d' % i)

		@property
		def _Pars(self):
			target = self.target.eval()
			target = target and self.m.op(target)
			if not target or not hasattr(target, 'GetParamsWithFlag'):
				return []
			return target.GetParamsWithFlag('mappable')

		@property
		def menuNames(self): return [p.name for p in self._Pars]

		@property
		def menuLabels(self): return [p.label for p in self._Pars]
