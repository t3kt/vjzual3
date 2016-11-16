print('common/popup_menu.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base

import json

class PopupMenu(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	def BuildMenuItems(self, dat):
		dat.clear()
		dat.appendRow(['text', 'action', 'help'])
		if self.comp.par.Usepar:
			self._AddParMenuItems(dat)
		else:
			self._AddJsonMenuItems(dat)

	def _AddJsonMenuItems(self, dat):
		itemsjson = self.comp.par.Menuitemsjson.eval()
		if not itemsjson:
			itemsjson = self.comp.op('./default_menu_items_json').text
		items = json.loads(itemsjson)
		for item in items:
			dat.appendRow([
				item.get('text', ''),
				item.get('action', ''),
				item.get('help', ''),
			])

	@property
	def _TargetPar(self):
		targetop = self.comp.par.Targetop.eval()
		parname = self.comp.par.Targetpar.eval()
		if not targetop or not parname:
			return None
		return getattr(targetop.par, parname, None)

	def _AddParMenuItems(self, dat):
		par = self._TargetPar
		if par is None or not par.isMenu:
			return
		for name, label in zip(par.menuNames, par.menuLabels):
			dat.appendRow([label, 'targetop.par.%s = %r' % (par.name, name), ''])

	@property
	def _MenuItems(self):
		return self.comp.op('./menu_items')

	@property
	def _MaxMenuItemLength(self):
		return max([len(c.val) for c in self._MenuItems.col('text')[1:]])

	@property
	def MenuWidth(self):
		if not self.comp.par.Useautowidth:
			return self.comp.par.Width.eval()
		itemlen = self._MaxMenuItemLength
		w = itemlen * self.comp.par.Widthperchar
		maxw = self.comp.par.Maxwidth.eval()
		if maxw > 0:
			return min(w, maxw)
		return w

	def UpdateParamStates(self):
		useauto = self.comp.par.Useautowidth.eval()
		self.comp.par.Width.enable = not useauto
		self.comp.par.Maxwidth.enable = useauto
		self.comp.par.Widthperchar.enable = useauto

		self.comp.par.Targetpar.enable = self.comp.par.Usepar

	def ExecuteAction(self, actioncode):
		if not actioncode:
			return
		targetop = self.comp.par.Targetop.eval()
		exec(actioncode, None, {'targetop': targetop})
		self.comp.par.Close.pulse()
