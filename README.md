# tektshell
Shell is a framework for modular TouchDesigner applications.

A shell application consists of:
* A tree of modules, where a module is a video effect, a generative renderer, a video input, grouping of other modules, etc.
* Shared infrastructure that supports features such as MIDI mapping, loading/saving state, output recording.

## modules
A module is a component consisting of:
* A common Python extension class (or sub-class thereof).
* A module shell subcomponent, which
  * provides common UI elements such as a collapsible header with bypass/solo/etc toggles
  * stores settings for the module such as which parameters to load/save and whether it has any viewers or advanced parameters.
* Optionally a control mappings component, which supports MIDI mappings
* Optionally a presets component, which loads/saves a set of named configurations
* Optionally audio/video/control signal inputs/outputs
* Optionally a group or chain of submodules
* Optionally UI controls bound to its parameters

Most modules are loaded as .tox files into a common location and then cloned. Some modules are defined in-place (instead of being cloned), such as groupings/chains of other modules or modules that are too specific to be useful as a reusable component.

