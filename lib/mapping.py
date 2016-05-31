print('shell/mapping.py initializing')

try:
	import common_base as base
except ImportError:
	import base
try:
	import common_util as util
except ImportError:
	import util

# if False:
# 	try:
# 		from _stubs import *
# 	except ImportError:
# 		from common.lib._stubs import *

# class ControlMappings(base.Extension):
# 	def __init__(self, comp):
# 		super().__init__(comp)
#
# 	@property
# 	def ControlTable(self):
# 		table = self.comp.par.Ctrltable.eval()
# 		if table:
# 			return table.path
# 		table = self.comp.op(self.comp.var('ctrltable'))
# 		return table.path if table else ''

def _GetHost(comp, settings):
	return comp.op(settings['hostop', 1]) or comp

def _GetMappingsFromHost(hostop):
	return hostop.fetch('ctrlMappings', {}, search=False)

def LoadMappings(comp, settings, dat):
	hostop = _GetHost(comp, settings)
	mapnames = util.ParseStringList(comp.par.Mapnames.eval())
	mappings = _GetMappingsFromHost(hostop)
	dat.clear()
	dat.appendRow(['name', 'ctrl', 'on'])
	for name in mapnames:
		mapping = mappings.get(name, {})
		dat.appendRow([
			name,
			mapping.get('ctrl') or '',
			1 if mapping.get('on') else 0,
		])
	for name, mapping in mappings.items():
		if name in mapnames:
			continue
		dat.appendRow([
			name,
			mapping.get('ctrl'),
			1 if mapping.get('on') else 0,
		])

# def UpdateMapping(comp, settings, name, ctrl, on):
# 	hostop = comp.op(settings['hostop', 1]) or comp
# 	mappings = hostop.fetch('ctrlMappings', {}, search=False)
# 	mappings[name] = {
# 		'ctrl': ctrl,
# 		'on': on,
# 	}
# 	hostop.store('ctrlMappings', mappings)

def StoreMappings(comp, settings, dat):
	hostop = _GetHost(comp, settings)
	mappings = _GetMappingsFromHost(hostop)
	for name in dat.col('name')[1:]:
		name = name.val
		mappings[name] = {
			'ctrl': dat[name, 'ctrl'].val,
			'on': dat[name, 'on'] == '1',
		}
	hostop.store('ctrlMappings', mappings)

def FillMappingNamesTable(comp, settings, dat):
	hostop = _GetHost(comp, settings)
	mappings = _GetMappingsFromHost(hostop)
	names, ctrls = [], []
	for name, mapping in mappings.items():
		ctrl = mapping.get('ctrl')
		if mapping.get('on') and ctrl:
			names.append(name)
			ctrls.append(ctrl)
	dat.clear()
	dat.appendRow([' '.join(names)])
	dat.appendRow([' '.join(ctrls)])
