print('common/base.py initializing')

try:
	import common_util as util
except ImportError:
	import util

class Extension:
	def __init__(self, comp):
		self.comp = comp

	def _GetId(self):
		return self.comp.par.opshortcut.eval() or self.comp.name

	@property
	def _MasterPath(self):
		master = self.comp.par.clone.eval()
		return master.path if master else self.comp.path

	def _LogEvent(self, event):
		util.Log('%s [%s] %s' % (self.comp.path, self._GetId() or '', event))
