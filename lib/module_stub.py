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
	def __init__(self, comp):
		self.comp = comp

	@property
	def IsModuleStub(self): return True

	@property
	def HasApp(self): return False

	def _NotSupported(self, action, iserror=False):
		message = 'Unsupported action: {}'.format(action)
		print('[{}] ModuleStub: {}'.format(self.comp.path, message))
		if iserror:
			raise Exception(message)

	def ResetState(self): self._NotSupported('ResetState')

	def UpdateHeight(self): self._NotSupported('UpdateHeight')

	def GetSchema(self, **_): self._NotSupported('GetSchema', iserror=True)

	def UpdateSolo(self): self._NotSupported('UpdateSolo')

	def BuildDefaultParameterMetadata(self, *_): self._NotSupported('BuildDefaultParameterMetadata')

	def GetParameterMetadata(self, parname): self._NotSupported('GetParameterMetadata({0!r})'.format(parname))

	def GetParamsWithFlag(self, flag, **kwargs):
		self._NotSupported('GetParamsWithFlag({0!r}, {1!r})'.format(flag, kwargs))
		return []

	@property
	def SubModuleOpNames(self): return []

	@property
	def SelectorOpNames(self):
		return [s.name for s in self.comp.findChildren(depth=1, parName='clone', parValue='*_selector')]

	@property
	def ExposedModParamNames(self): return []

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
