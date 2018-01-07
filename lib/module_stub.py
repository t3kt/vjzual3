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
		if self.realmod:
			self.realmod.UpdateHeight()
		else:
			self._NotSupported('UpdateHeight')

	def GetSchema(self, **kwargs):
		if self.realmod:
			return self.realmod.GetSchema(**kwargs)
		else:
			self._NotSupported('GetSchema', iserror=True)

	def UpdateSolo(self):
		if self.realmod:
			self.realmod.UpdateSolo()
		else:
			self._NotSupported('UpdateSolo')

	def BuildDefaultParameterMetadata(self, *args):
		if self.realmod:
			self.realmod.BuildDefaultParameterMetadata(*args)
		else:
			self._NotSupported('BuildDefaultParameterMetadata')

	def GetParameterMetadata(self, parname):
		if self.realmod:
			return self.realmod.GetParameterMetadata(parname)
		else:
			self._NotSupported('GetParameterMetadata({0!r})'.format(parname))

	def GetParamsWithFlag(self, flag, **kwargs):
		if self.realmod:
			return self.realmod.GetParamsWithFlag(flag, **kwargs)
		else:
			self._NotSupported('GetParamsWithFlag({0!r}, {1!r})'.format(flag, kwargs))
			return []

	@property
	def SubModuleOpNames(self): return self.realmod.SubModuleOpNames if self.realmod else []

	@property
	def SelectorOpNames(self):
		return [s.name for s in self.comp.findChildren(depth=1, parName='clone', parValue='*_selector')]

	@property
	def ExposedModParamNames(self): return self.realmod.ExposedModParamNames if self.realmod else []

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
