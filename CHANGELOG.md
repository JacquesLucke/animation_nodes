## Unreleased

### Added

- Added *Set Vertex Weight* node.
- Added CList and VirtualList for colors.
- Added Get Vertex Color Layer node.
- Added Insert Vertex Color Layer node.
- Added Get Linked Vertices node.
- Added Set Bevel Vertex Weight node.
- Added Set Bevel Edge Weight node.
- Added Vector 2D and Vector 2D List sockets.
- Added VirtualVector2DList structure.
- Added Get UV Map node.
- Added Insert UV Map node.
- Added Set UV Map node.

### Fixed

- Fixed sound nodes when sounds are packed in the blend file.
- Fixed the *Frame Rate* output of the *Time Info* node.
- Fixed sound evaluation when sound sequences are cut.
- Fixed *Set Vertex Color* node when alpha value change.
- Fixed time measurement. `time.clock()` was removed in python 3.8.
- Fixed the Node Editor's HUD position.
- Fixed Curve Interpolation node.
- Fixed the name output in the Mesh Object Input node.
- Fixed Slice List node for negative start index in Length mode.
- Fixed duplication of the Curve Interpolation node.
- Fixed the Ensure Animation Data option in the Mesh Object Output node.
- Fixed crashes during rendering and exporting.
- Fixed inconsistency between viewport, renders, and exports.

### Changed

- Allow getting items from virtual lists in Python.
- Allow choosing alpha in Color socket.
- Update initialization error messages.
- Normalize Quaternion in the *Combine Quaternion* node.
- Normalize Quaternion in the *Convert Rotations* node.
- Vectorized Set Vertex Color node and color modes are added.
- Linux and MacOS are now release builds. They were debug builds.
- Added Points mode to the Line Mesh node.
- Added the `__repr__` function for spline.

## 2.1.5

### Added

- Added *Include End Point* option to the *Float Range* node.
- Added collection option to *Execution Triggers*.
- Added *Sound Falloff* node.
- Added *Subprograms* to the search menu.
- Added missing nodes to the node menu
- Added *Collection Operations* node.
- Added *Rotations* output to the *Particles Data* node.

### Fixed

- Fixed the *Sort* node for Windows users.
- Fixed bad path resolution in the *Set Keyframe* node.
- Fixed *Convert Plane Type* node.
- Fixed *ReturnDefaultsOnExceptionCodeEffect* and *Get Struct* node.
- Fixed the *fromFloatList* method of the *3DVectorList* structure.
- Fixed double period in the description of some properties.
- Fixed *Material Output* node's color output.
- Fixed *Create Execution Trigger* operators.
- Fixed *getSelectedObjectNames* function.
- Fixed the *Offset Vertices* and *Offset Polygons* nodes. Copy the input mesh if needed.
- Fixed bad precision in the *Wiggle Falloff* node.
- Fixed header alignment for the *Subprograms* menu and the *Remove* nodetree operator.

### Changed

- Redesigned *Execution Triggers* UI.
- Allow multiple comma separated data paths per *Execution Trigger*.
- Replaced colored icons in the *Node Menu* to be more uniform.
- Started following Blender's class naming conventions.
- Made dependent nodes unsearchable like *Loop Generator* and *Group Output* nodes.
- Changed location of Animation Nodes to Animation Nodes Editor.
- Allow spline radius to affect the object's scale in the Follow Spline Action.
- Vectorized the *Number Wiggle*, *Euler Wiggle*, and *Quaternion Wiggle* nodes.
- Inform the user that no *Viewport Input* node exist in the *Data Input* panel.
