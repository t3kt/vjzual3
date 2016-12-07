print('shell/clips.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base

try:
	import common_ctrl as ctrl
except ImportError:
	try:
		import ctrl
	except ImportError:
		import common.lib.ctrl as ctrl

if False:
	try:
		from _stubs import *
	except ImportError:
		from common.lib._stubs import *

_LABEL_COL = 0
_PREVIEW_COL = 1
_LOAD_BUTTON_COL = 2
_EDIT_BUTTON_COL = 3
_BUTTON_COLS = [_LOAD_BUTTON_COL, _EDIT_BUTTON_COL]

class ClipBin(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	@property
	def _Clips(self):
		return self.comp.op('./clips')

	def _GetPreviewTOP(self, num):
		return self.comp.op('./clip_previews/preview__%d' % num)

	@property
	def _Previews(self):
		return self.comp.op('./clip_previews')

	@property
	def _BgColor(self):
		return 0, 0, 0, 1

	@property
	def _RolloverBgColor(self):
		return 0.3, 0.3, 0.3, 1

	@property
	def _ButtonBgColor(self):
		return 0.4, 0.4, 0.4, 1

	@property
	def _ButtonRolloverBgColor(self):
		return 0.8, 0.8, 0.8, 1

	def List_onInitTable(self, listcomp, attribs):
		pass

	def List_onInitCol(self, listcomp, col, attribs):
		if col == _LABEL_COL:
			attribs.colStretch = True
		elif col == _PREVIEW_COL:
			attribs.colWidth = 100
		elif col in _BUTTON_COLS:
			attribs.colWidth = 30
			attribs.bgColor = self._ButtonBgColor

	def List_onInitRow(self, listcomp, row, attribs):
		if row == 0:
			attribs.leftBorderOutColor = attribs.rightBorderOutColor =\
				attribs.topBorderOutColor = attribs.bottomBorderOutColor = (.1, .1, .1, 1)
			attribs.bgColor = (0.9, 0.9, 0.9, 1)
		else:
			attribs.leftBorderOutColor = attribs.rightBorderOutColor =\
				attribs.topBorderOutColor = attribs.bottomBorderOutColor = (.5, .5, .5, 1)
			attribs.rowHeight = 80

	def List_onInitCell(self, listcomp, row, col, attribs):
		# self._LogEvent('List_onInitCell(row: %r, col: %r)' % (row, col))
		if row == 0:
			return
		if col == _LABEL_COL:
			attribs.text = self._Clips[row, 'name']
			attribs.textJustify = JustifyType.TOPLEFT
			attribs.wordWrap = True
		elif col == _PREVIEW_COL:
			thumb = self._GetPreviewTOP(row)
			attribs.top = thumb if thumb else ''
			attribs.bgColor = self._BgColor
		elif col == _LOAD_BUTTON_COL:
			attribs.wordWrap = True
			attribs.text = 'L\no\na\nd'
		elif col == _EDIT_BUTTON_COL:
			attribs.wordWrap = True
			attribs.text = 'E\nd\ni\nt'

	def List_onRollover(self, listcomp, row, col, prevrow, prevcol):
		# self._LogEvent('onRollover(row: %r, col: %r, prevrow: %r, prevcol: %r)' % (row, col, prevrow, prevcol))
		previews = self._Previews
		if prevrow and prevrow != -1:
			listcomp.cellAttribs[prevrow, _LABEL_COL].bgColor = self._BgColor
			for btncol in _BUTTON_COLS:
				listcomp.cellAttribs[prevrow, btncol].bgColor = None

		if row and row != -1:
			listcomp.cellAttribs[row, _LABEL_COL].bgColor = self._RolloverBgColor
			for btncol in _BUTTON_COLS:
				listcomp.cellAttribs[row, btncol].bgColor = self._ButtonRolloverBgColor if col == btncol else None
			previews.par.Activeclip = row
		else:
			previews.par.Activeclip = 0

	# def _StartStopPreview(self, num, on):
	# 	if not num or num == -1:
	# 		return
	# 	top = self._GetPreviewTOP(num)
	# 	if not top:
	# 		return
	# 	if on:
	# 		if not top.par.play:
	# 			top.par.play = True
	# 			top.par.cue.pulse()
	# 	else:
	# 		if top.par.play:
	# 			top.par.play = False

	def List_onSelect(self, listcomp, startrow, startcol, startcoords, endrow, endcol, endcoords, start, end):
		pass


# attribs contains the following members:
#
# text				   str            cell contents
# help                 str       	  help text
#
# textColor            r g b a        font color
# textOffsetX		   n			  horizontal text offset
# textOffsetY		   n			  vertical text offset
# textJustify		   m			  m is one of:  JustifyType.TOPLEFT, JustifyType.TOPCENTER,
#                                                   JustifyType.TOPRIGHT, JustifyType.CENTERLEFT,
#                                                   JustifyType.CENTER, JustifyType.CENTERRIGHT,
#                                                   JustifyType.BOTTOMLEFT, JustifyType.BOTTOMCENTER,
#                                                   JustifyType.BOTTOMRIGHT
#
# bgColor              r g b a        background color
#
# leftBorderInColor	   r g b a		  inside left border color
# rightBorderInColor   r g b a		  inside right border color
# topBorderInColor	   r g b a		  inside top border color
# bottomBorderInColor  r g b a		  inside bottom border color
#
# leftBorderOutColor   r g b a		  outside left border color
# rightBorderOutColor  r g b a		  outside right border color
# topBorderOutColor	   r g b a		  outside top border color
# bottomBorderOutColor r g b a		  outside bottom border color
#
# colWidth             w              sets column width
# colStetch            True/False     sets column stretchiness (width is min width)
# rowHeight            h              sets row height
#
# editable			   int			  number of clicks to activate editing the cell.
# fontBold             True/False     render font bolded
# fontItalic           True/False     render font italicized
# fontSizeX            float		  font X size in pixels
# fontSizeX            float		  font Y size in pixels, if not specified, uses X size
# fontFace             str			  font face, example 'Verdana'
# wordWrap             True/False     word wrap
#
# top                  TOP			  background TOP operator
#
# select   true when the cell/row/col is currently being selected by the mouse
# rollover true when the mouse is currently over the cell/row/col
# radio    true when the cell/row/col was last selected
# focus    true when the cell/row/col is being edited
#
# currently not implemented:
#
# type                str             cell type: 'field' or 'label'
# fieldtype           str             field type: 'float' 'string' or  'integer'
# setpos              True/False x y  set cell absolute when first argument is True
# padding             l r b t         cell padding from each edge, expressed in pixels
# margin              l r b t         cell margin from neighbouring cells, expressed in pixels
#
# fontpath            path            File location to font. Don't use with 'font'
# fontformat          str             font format: 'polygon', 'outline' or 'bitmap'
# fontantialiased     True/False      render font antialiased
# fontcharset         str             font character set
#
# textjustify         h v             left/right/center top/center/bottom
# textoffset          x y             text position offset
#

