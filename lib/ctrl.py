if False:
	import util
else:
	import core_util as util

print('core ctrl.py initializing')

def GetTargetPar(ctrl):
	targetOp = ctrl.par.Targetop.eval()
	if not targetOp:
		return
	parName = ctrl.par.Targetpar.eval()
	if not parName:
		return
	return getattr(targetOp.par, parName, None)
