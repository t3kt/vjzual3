def setupParameters(dat):
	#dat.destroyCustomPars()
	page = dat.appendCustomPage('Custom')
	page.appendFloat('Offset', label='Offset (frames)')
	pass

import xml.etree.ElementTree as ET

def cook(dat):
	dat.clear()
	dat.appendRow(['name', 'track', 'label', 'start_sec', 'end_sec', 'length_sec', 'start_frame', 'end_frame', 'length_frame'])
	root = ET.fromstring(dat.inputs[0].text)
	labelTracks = root.findall('./a:labeltrack', {"a": "http://audacity.sourceforge.net/xml/"})
	fps = float(var('FPS'))
	offsetsec = dat.par.Offset.eval() / fps
	for labelTrack in labelTracks:
		trackName = labelTrack.attrib['name']
		for label in labelTrack.findall('./a:label', {"a": "http://audacity.sourceforge.net/xml/"}):
			title = label.attrib['title']
			t0sec, t1sec = float(label.attrib['t']), float(label.attrib['t1'])
			t0sec += offsetsec
			t1sec += offsetsec
			dat.appendRow([
				trackName + '/' + title,
				trackName,
				title,
				t0sec,
				t1sec,
				t1sec - t0sec,
				int(fps * t0sec),
				int(fps * t1sec),
				int(fps * (t1sec-t0sec))
			])