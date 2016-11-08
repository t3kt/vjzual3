print('shell/MenuTableBuilder.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base

class MenuTableBuilder(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def _SourceParams(self):
		srcop = self.comp.par.Sourceop.eval()
		if not srcop:
			return []
		return [(p.name, p.label) for p in srcop.pars('*') if p.isMenu]

	def UpdateSourceParMenu(self):
		params = self._SourceParams
		parpar = self.comp.par.Sourcepar
		parpar.menuNames = [name for name, label in params]
		parpar.menuLabels = ['%s (%s)' % (label, name) for name, label in params]

	@property
	def _MenuItems(self):
		srcop = self.comp.par.Sourceop.eval()
		srcpar = srcop.pars(self.comp.par.Sourcepar.eval()) if srcop else None
		if not srcpar:
			return []
		srcpar = srcpar[0]
		return [
			(name, srcpar.menuLabels[i])
			for i, name in enumerate(srcpar.menuNames)
		]

	def BuildMenuTable(self, dat):
		dat.clear()
		items = self._MenuItems
		fmt = self.comp.par.Tableformat.eval()
		if fmt == 'gal':
			dat.appendRow(['name', 'short', 'token', 'icon', 'command'])
			for name, label in items:
				dat.appendRow([name, label.replace(' ', ''), name, '', ''])
				pass
		elif fmt == 'raw':
			for item in items:
				dat.appendRow(item)
		else:
			dat.appendRow(['name', 'label'])
			for item in items:
				dat.appendRow(item)
