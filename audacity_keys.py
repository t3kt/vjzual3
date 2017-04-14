def setupParameters(dat):
	page = dat.appendCustomPage('Custom')
	p = page.appendInt('Width', label='Pulse Width')[0]
	p.min = 1
	p.normMin = 1
	p.clampMin = True
	p.normMax = 20
	p = page.appendInt('Id', label='ID')[0]
	p.min = 1
	p.normMin = 1
	p.clampMin = True
	p.normMax = 20
	page.appendToggle('Overridewidth', label='Override Width')
	pass


def cook(dat):
	dat.clear()
	dat.appendRow(['id', 'x', 'y', 'inslope', 'inaccel', 'expression', 'outslope', 'outaccel'])
	width = dat.par.Width.eval()
	chanId = dat.par.Id.eval()
	addRow(dat, chanId, 0, 0)
	overrideWidth = dat.par.Overridewidth.eval()
	indat = dat.inputs[0]
	if indat.numRows < 2:
		return
	for i in range(1, indat.numRows):
		begin = float(indat[i, 'start_frame'])
		if overrideWidth:
			end = begin + width
		else:
			end = float(indat[i, 'end_frame'])
		addRow(dat, chanId, begin, 1)
		addRow(dat, chanId, end, 0)
	addRow(dat, chanId, end + 10, 0)

# def _addTrack(dat, chanId, )

def addRow(dat, chanId, time, value):
	# id	x	y	inslope	inaccel	expression	outslope	outaccel
	dat.appendRow([
		chanId,
		time,  # x
		value,  # y
		0,  # inslope
		0,  # inaccel
		'constant()',  # expression
		0,  # outslope
		0,  # outaccel
	])
