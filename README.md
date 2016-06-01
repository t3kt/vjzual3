# tektshell
Shell is a framework for modular TouchDesigner applications.

*(Not all functionality described in this document has been implemented)*

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
* Optionally audio/video inputs/outputs
* Optionally a group or chain of submodules
* Optionally UI controls bound to its parameters
* Optional *data nodes* (see below)

Most modules are loaded as .tox files into a common location and then cloned. Some modules are defined in-place (instead of being cloned), such as groupings/chains of other modules or modules that are too specific to be useful as a reusable component.

## data nodes and selectors
While simple modules can use a single audio/video input and output, some modules need to use multiple sources of audio/video. For example, a displacement module needs a secondary source of video used to distort the main input. To support this, the *data node* system provides a centralized list of data nodes (a/v sources) located in the various modules in an application. The *data selector* component provides a UI for selecting from this list of sources and retrieving the associated a/v stream, along with a viewer that shows the content of the stream. A *data node* is defined by a clone of the *data node* component, which has a globally unique ID and is associated with a video source (TOP) and/or audio source (CHOP).

