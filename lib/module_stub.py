def IsHosted():
	try:
		getattr(mod, 'shell_module')
	except ImportError:
		return False
	return True

def CreateModule(comp):
	if IsHosted():
		return mod.shell_module.Module(comp)
	else:
		print('Unable to create proper module extension without shell host: {}'.format(comp))
		return ModuleStub(comp)

class ModuleStub:
	def __init__(self, comp, realmod=None):
		self.comp = comp
		self._realmod = realmod

	@property
	def realmod(self):
		if self._realmod:
			return self._realmod
		elif IsHosted():
			modtype = mod.shell_module.Module
			for ext in self.comp.extensions:
				if isinstance(ext, modtype):
					self._realmod = ext
					break
		return self._realmod

	@property
	def IsModuleStub(self): return self.realmod is None

	@property
	def HasApp(self):
		return self.realmod.HasApp if self.realmod else False

	def _NotSupported(self, action, iserror=False):
		message = 'Unsupported action: {}'.format(action)
		print('[{}] ModuleStub: {}'.format(self.comp.path, message))
		if iserror:
			raise Exception(message)

	def ResetState(self):
		if self.realmod:
			self.realmod.ResetState()
		else:
			self._NotSupported('ResetState')

	def UpdateHeight(self):
		self._NotSupported('UpdateHeight', iserror=False)
		shell = self.comp.op('./shell')
		UpdateModuleHeight(
			self.comp,
			autoheight=shell.par.Autoheight if shell else True)

	def UpdateSolo(self):
		if self.realmod:
			self.realmod.UpdateSolo()
		else:
			self._NotSupported('UpdateSolo')

	def BuildDefaultParameterMetadata(self, *args):
		if self.realmod:
			self.realmod.BuildDefaultParameterMetadata(*args)
		else:
			self._NotSupported('BuildDefaultParameterMetadata', iserror=False)

	def GetParamsWithFlag(self, flag, **kwargs):
		if self.realmod:
			return self.realmod.GetParamsWithFlag(flag, **kwargs)
		else:
			self._NotSupported('GetParamsWithFlag({0!r}, {1!r})'.format(flag, kwargs), iserror=False)
			return []

	@property
	def SubModuleOpNames(self): return self.realmod.SubModuleOpNames if self.realmod else []

	@property
	def SelectorOpNames(self):
		return [s.name for s in self.comp.findChildren(depth=1, parName='clone', parValue='*_selector')]

	@property
	def ExposedModParamNames(self):
		self._NotSupported('ExposedModParamNames', iserror=False)
		return []

def ParseStringList(val):
	if not val:
		return []
	if val.startswith('['):
		return mod.json.loads(val)
	else:
		for sep in [',', ' ']:
			if sep in val:
				return [v.strip() for v in val.split(sep) if v.strip()]
		return [val]

def _GetVisibleCOMPsHeight(comps):
	return sum([o.par.h for o in comps if getattr(o, 'isPanel', False) and o.par.display])

def _GetVisibleChildCOMPsHeight(parentOp):
	return _GetVisibleCOMPsHeight([c.owner for c in parentOp.outputCOMPConnectors[0].connections])

def UpdateModuleHeight(comp, autoheight=True):
	ctrlpanel = comp.op('./controls_panel')
	bodypanel = comp.op('./body_panel')
	if ctrlpanel:
		ctrlpanel.par.h = _GetVisibleChildCOMPsHeight(ctrlpanel)
	collapsed = comp.par.Collapsed.eval() if hasattr(comp.par, 'Collapsed') else False
	headerheight = 20 if collapsed else 40
	if autoheight:
		if bodypanel:
			bodypanel.par.h = _GetVisibleChildCOMPsHeight(bodypanel)
		h = headerheight
		if not collapsed:
			h += bodypanel.height if bodypanel else 20
		comp.par.h = h
	else:
		if bodypanel:
			bodypanel.par.h = comp.height - headerheight
