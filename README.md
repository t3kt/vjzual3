# tektcore
tektcore is a library of components for use in TouchDesigner projects. It contains the infrastructure to support projects and to build control UIs.

## things that tektcore should/does include:
* very general-purpose python utilities, `setattrs()`, things for common DAT manipulation/scanning, etc.
* UI controls that bind to OP parameters (or standalone without a parameter)

## things that tektcore should *not* include:
* video effects - they end up generating cruft over time since you can't change the effects later without potentially changing other projects
* geometry stuff
* obscure and overly-specific utility functions

## host project assumptions/requirements
* project root OP is `/_`
* `/_/local` COMP contains with project-wide variables specified inside
* `$coredir` contains absolute path to the directory that contains the core components, without a trailing slash. example: `$TOUCH/core`
* `/_/core` COMP contains the components and resources imported from the core directory
