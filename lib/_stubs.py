# trick pycharm
mod = object()
ui = object()
ui.panes = []
ui.panes.current = None
ui.status = ''
PaneType = object()
PaneType.NETWORKEDITOR = None
project = object()
project.name = ''

def op(path):
	return object()

def ops(*paths):
	return []

def var(name):
	return ''

td = object()

class _TD_ERROR(Exception):
	pass

td.error = _TD_ERROR

del _TD_ERROR
