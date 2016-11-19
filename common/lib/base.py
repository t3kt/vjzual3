print('common/base.py initializing')

try:
	import common_util as util
except ImportError:
	import util

class IndentedLogger:
	def __init__(self):
		self._indentLevel = 0
		self._indentStr = ''

	def _AddIndent(self, amount):
		self._indentLevel += amount
		self._indentStr = '\t' * self._indentLevel

	def Indent(self):
		self._AddIndent(1)

	def Unindent(self):
		self._AddIndent(-1)

	def LogEvent(self, path, opid, event):
		util.Log('%s [%s] %s (%s)' % (self._indentStr, opid or '', event, path or ''))

	def LogBegin(self, path, opid, event):
		self.LogEvent(path, opid, event)
		self.Indent()

	def LogEnd(self, path, opid, event):
		self.Unindent()
		if event:
			self.LogEvent(path, opid, event)

logger = IndentedLogger()

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
		logger.LogEvent(self.comp.path, self._GetId(), event)

	def _LogBegin(self, event):
		logger.LogBegin(self.comp.path, self._GetId(), event)

	def _LogEnd(self, event=None):
		logger.LogEnd(self.comp.path, self._GetId(), event)


