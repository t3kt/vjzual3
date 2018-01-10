print('shell/app.py initializing')

try:
	import common_base as base
except ImportError:
	try:
		import base
	except ImportError:
		import common.lib.base as base
try:
	import shell_nodes as nodes
except ImportError:
	import nodes

if False:
		from _stubs import *

class ShellApp(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.DataNodeBank = comp.par.Datanodebank.eval()

	def ResetState(self):
		self._LogBegin('ResetState()')
		try:
			for child in self._SubModules:
				child.ResetState()
		finally:
			self._LogEnd('ResetState()')

	@property
	def AllModules(self):
		return self.comp.findChildren(type=COMP, tags=['tmod'])

	@property
	def _SubModules(self):
		return self.comp.findChildren(type=COMP, tags=['tmod'], depth=1)

	@property
	def OutputSource(self):
		g = getattr(op, 'Global', None)
		if g is None:
			return None
		return g.par.Source

	@property
	def _Key(self):
		return self.comp.par.Schemakey.eval() or project.name.replace('\.toe', '')

	@property
	def _Title(self):
		return self.comp.par.Title.eval() or self._Key

	def GetSchema(
			self,
			addmissingmodtypes=True):
		self._LogEvent('GetSchema(addmissingmodtypes=%r)' % addmissingmodtypes)
		builder = _VjzAppSchemaBuilder(
			app=self,
			comp=self.comp,
			addmissingmodtypes=addmissingmodtypes,
		)
		return builder.BuildAppSchema()


def _LoadSchemaMod():
	try:
		return mod.shell_schema
	except ImportError:
		return None


schema = _LoadSchemaMod()

if schema is not None:
	class _VjzAppSchemaBuilder(schema.AppSchemaBuilder):
		def __init__(
				self,
				app,
				comp,
				addmissingmodtypes=True):
			super().__init__(
				comp=comp,
				key=app._Key,
				label=comp.par.Title.eval(),
				tags=[],
				addmissingmodtypes=addmissingmodtypes,
			)
			self.app = app

		def _BuildConnections(self):
			return [
				schema.ConnectionInfo(
					conntype='oscin',
					port=self.comp.par.Oscinport.eval(),
				),
				schema.ConnectionInfo(
					conntype='oscout',
					host=self.comp.par.Oscouthost.eval() or self.comp.par.Oscouthost.default,
					port=self.comp.par.Oscoutport.eval(),
				)
			]

		def _GetChildModules(self):
			return sorted(self.app._SubModules, key=lambda m: m.par.order)

		def _BuildChildModuleSchema(self, childcomp):
			builder = schema.VjzModuleSchemaBuilder(
				comp=childcomp,
				pathprefix=self.pathprefix,
				appbuilder=self,
				addmissingmodtypes=self.addmissingmodtypes,
			)
			return builder.BuildModuleSchema()

		def _BuildModuleTypeSchema(self, typename):
			childcomp = self.comp.op(typename)
			builder = schema.VjzModuleSchemaBuilder(
				comp=childcomp,
				pathprefix=self.pathprefix,
				appbuilder=self,
				addmissingmodtypes=False,
			)
			return builder.BuildModuleTypeSchema()

		def _BuildOptionLists(self):
			return [
				schema.OptionList(
					'sources',
					label='Sources',
					options=[
						schema.ParamOption(n['id'], n['label'])
						for n in nodes.GetAppNodes()
						]
				)
			]
else:
	class _VjzAppSchemaBuilder:
		def __init__(self, *args, **kwargs):
			pass

		def BuildAppSchema(self):
			pass




