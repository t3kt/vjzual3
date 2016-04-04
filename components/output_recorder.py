import datetime
import glob
import os.path
import re
if False:
	from _stubs import *

print('core output_recording.py initializing')

class OutputRecorderExt:
	def __init__(self, comp):
		self.comp = comp

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

	def CaptureImage(self):
		f = self.NextFileName + '.' + self.comp.par.Imageext
		print('saving image ' + f)
		self.comp.op('video').save(f)
		ui.status = 'saved image ' + f
		self._UpdateFileNameLabel()

	def StartVideoCapture(self):
		f = self.NextFileName + '.' + self.comp.par.Videoext
		m = self.comp.op('moviefileout')
		print('starting video recording ' + f)
		m.par.file = f
		m.par.record = 1
		self._UpdateFileNameLabel()

	def EndVideoCapture(self):
		m = self.comp.op('moviefileout')
		f = m.par.file
		print('finished video recording ' + f)
		ui.status = 'saved video ' + f
		m.par.record = 0
		self._UpdateFileNameLabel()

	def _UpdateFileNameLabel(self):
		pass

def _getIndex(f):
	return int(re.match(r'.+-([0-9]+)(-.+)?\.[0-9a-z]+', f).group(1))

