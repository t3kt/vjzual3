if False:
	import util
else:
	import core_util as util

import json

print('core ctrl.py initializing')

def GetTargetPar(ctrl):
	if not ctrl:
		return
	targetOp = ctrl.par.Targetop.eval()
	if not targetOp:
		return
	parName = ctrl.par.Targetpar.eval()
	if not parName:
		return
	return getattr(targetOp.par, parName, None)

def ParseStringList(val):
	if not val:
		return []
	if val.startswith('['):
		return json.loads(val)
	elif ',' in val:
		return [v.strip() for v in val.split(',') if v.strip()]
	else:
		return [val]
