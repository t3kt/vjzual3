# tektcommon
tektcommon is a library of components for use in TouchDesigner projects. It contains the infrastructure to support projects and to build control UIs.

## things that tektcommon should/does include:
* very general-purpose python utilities, `setattrs()`, things for common DAT manipulation/scanning, etc.
* UI controls that bind to OP parameters (or standalone without a parameter)

## things that tektcommon should *not* include:
* video effects - they end up generating cruft over time since you can't change the effects later without potentially changing other projects
* geometry stuff
* obscure and overly-specific utility functions
* **dependencies on anything else**
  * It should be *really really simple* to drop tektcommon into a project. Dependencies make that more complicated and error-prone.

## host project assumptions/requirements
* project root OP is `/_`
* `/_/local` COMP contains with project-wide variables specified inside
* `$commondir` contains absolute path to the directory that contains the common components, without a trailing slash. example: `$TOUCH/common`
* `/_/common` COMP contains the components and resources imported from the common directory
* `/local/modules` contains the common python modules (see common-tester.toe for example)
