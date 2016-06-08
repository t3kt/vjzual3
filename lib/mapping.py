print('shell/mapping.py initializing')

try:
	import common_base as base
except ImportError:
	import base
try:
	import common_util as util
except ImportError:
	import util

import ast

_STORAGE_KEY = 'ctrlMappings'

def _GetHost(comp, settings):
	return comp.op(settings['hostop', 1]) or comp

def GetMappingsFromHost(hostop):
	return hostop.fetch(_STORAGE_KEY, {}, search=False)

# def LoadMappings(comp, settings, dat):
# 	hostop = _GetHost(comp, settings)
# 	mapnames = util.ParseStringList(comp.par.Mapnames.eval())
# 	mappings = GetMappingsFromHost(hostop)
# 	dat.clear()
# 	dat.appendRow(['name', 'ctrl', 'on'])
# 	for name in mapnames:
# 		mapping = mappings.get(name, {})
# 		dat.appendRow([
# 			name,
# 			mapping.get('ctrl') or '',
# 			1 if mapping.get('on') else 0,
# 		])

def ConvertStorageTableToMappingsTable(storagedat, dat):
	dat.clear()
	dat.appendRow(['name', 'ctrl', 'on'])
	for key, val in storagedat.rows()[1:]:
		mapping = ast.literal_eval(val.val)
		if not mapping:
			mapping = {}
		dat.appendRow([key, mapping.get('ctrl', ''), 1 if mapping.get('on') else 0])

def LoadMappingsFromTable(comp, dat, opprefix):
	for i in range(1, dat.numRows):
		mname = dat[i, 'name']
		mapui = comp.op('./%s%s' % (opprefix, mname))
		if not mapui:
			# TODO: logging?
			continue
		ctrl = dat[i, 'ctrl'].val
		on = dat[i, 'on'] == '1'
		SetMappingValues(mapui, ctrl, on)

def FillMappingNamesTable(comp, dat):
	mapnames = util.ParseStringList(comp.par.Mapnames.eval())
	dat.clear()
	dat.appendCol(mapnames)

def StoreMappings(comp, settings, dat):
	hostop = _GetHost(comp, settings)
	mappings = {}
	for name in dat.col('name')[1:]:
		name = name.val
		ctrl = dat[name, 'ctrl']
		mappings[name] = {
			'ctrl': ctrl.val if ctrl is not None or ctrl == 'none' else '',
			'on': dat[name, 'on'] == '1',
		}
	hostop.store(_STORAGE_KEY, mappings)

def ClearMappings(comp, settings):
	hostop = _GetHost(comp, settings)
	hostop.unstore(_STORAGE_KEY)

def FillMappingNameSelectTable(comp, settings, dat):
	hostop = _GetHost(comp, settings)
	mappings = GetMappingsFromHost(hostop)
	names, ctrls = [], []
	for name, mapping in mappings.items():
		ctrl = mapping.get('ctrl')
		if mapping.get('on') and ctrl:
			names.append(name)
			ctrls.append(ctrl)
	dat.clear()
	dat.appendRow([' '.join(names)])
	dat.appendRow([' '.join(ctrls)])

def SetMappingLabel(mapui, name):
	mapui.op('./name_label').par.Label = name or ''

def SetMappingValues(mapui, ctrl, on):
	mapui.op('./ctrl_menu/ext').SetValue(ctrl or 'none')
	mapui.op('./on_button/ext').SetValue(on or False)

def DisconnectAllExceptHeader(merge, header):
	conns = list(merge.inputConnectors)
	for conn in conns:
		if len(conn.connections) == 0 or conn.connections[0].owner == header:
			continue
		while len(conn.connections):
			conn.disconnect()
