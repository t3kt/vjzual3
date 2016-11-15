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

	def BuildMenuItems(self, dat, defaultitemsjson):
		itemsjson = self.comp.par.Menuitemsjson.eval() or defaultitemsjson
		items = json.loads(itemsjson)
		dat.clear()
		dat.appendRow(['text', 'action', 'help'])
		for item in items:
			dat.appendRow([
				item.get('text', ''),
				item.get('action', ''),
				item.get('help', ''),
			])

	def ExecuteAction(self, actioncode):
		if not actioncode:
			return
		targetop = self.comp.par.Targetop.eval()
		exec(actioncode, None, {'targetop': targetop})
