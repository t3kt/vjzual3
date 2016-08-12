import datetime
import glob
import os.path
import re
if False:
	import util
else:
	import common_util as util
if False:
	from _stubs import *

print('common output_recording.py initializing')

class OutputRecorderExt:
	def __init__(self, comp):
		self.comp = comp
		self.UpdateParamStates()
		self.UpdateFileNameLabel()

	@property
	def BaseFileName(self):
		basename = self.comp.par.Basename.eval()
		if basename:
			return basename
		return os.path.splitext(project.name)[0] + '-output'

	@property
	def NextFileName(self):
		base = self.BaseFileName
		base += '-' + str(datetime.date.today()) + '-'
		files = glob.glob(base + '*')
		if len(files) == 0:
			return base + '1'
		i = max([_getIndex(f) for f in files]) + 1
		f = base + str(i)
		suffix = self.comp.par.Suffix.eval()
		if suffix:
			f += '-' + suffix
		return f

	@property
	def NextFileFullPath(self):
		name = self.NextFileName
		path = self.comp.par.Folder.eval()
		if not path:
			return name
		if not path.endswith('/'):
			path += '/'
		return path + name

	def CaptureImage(self):
		f = self.NextFileFullPath + '.' + self.comp.par.Imageext
		print('saving image ' + f)
		self.comp.op('video').save(f)
		ui.status = 'saved image ' + f
		self.UpdateFileNameLabel()

	def StartVideoCapture(self):
		f = self.NextFileFullPath + '.' + self.comp.par.Videoext
		m = self.comp.op('moviefileout')
		print('starting video recording ' + f)
		m.par.file = f
		m.par.record = 1
		self.UpdateFileNameLabel()

	def EndVideoCapture(self):
		m = self.comp.op('moviefileout')
		f = m.par.file
		print('finished video recording ' + f)
		ui.status = 'saved video ' + f
		m.par.record = 0
		self.UpdateFileNameLabel()

	def UpdateFileNameLabel(self):
		self.comp.op('nextfilename_value').par.Label = self.NextFileName

	def UpdateParamStates(self):
		useinput = self.comp.par.Useinputres.eval()
		self.comp.par.Resolution1.enable = not useinput
		self.comp.par.Resolution2.enable = not useinput

	def UpdateHeight(self):
		if self.comp.par.Autoheight:
			self.comp.par.h = max(util.GetVisibleChildCOMPsHeight(self.comp.op('root_panel')), 20)

def _getIndex(f):
	return int(re.match(r'.+-([0-9]+)(-.+)?\.[0-9a-z]+', f).group(1))

