## Unreleased

### Added

- Added GP Stroke From Spline node.
- Added Spline From GP Stroke node.
- Added Offset GP Stroke node.
- Added Polygon Indices List to Edge Indices List link conversion.
- Added Offset Spline Node.
- Added Grease Pencil type to the Object Instancer node.
- Added List to Element link conversion.
- Added GP sockets link conversions.
- Added input range to Remap Falloff node.
- Added Bmesh Invert Normals node.
- Added Object Material Input node.
- Added Vector Noise node to the node menu.
- Added *Use Spline Radius* option in *Spline Falloff* node.

### Fixed

- Fixed Decompose Text node for fonts relative path.
- Fixed fatal error when using replicate nodes.
- Fixed crash upon updating the Separate Text node when main collection is hidden.
- Fixed the New Text Block operator in the script node.
- Fixed enum callbacks by caching them.
- Fixed the Triangulate BMesh node.
- Fixed smooth sound spectrum evaluation.
- Fixed the None material issue of the Material Output node.
- Fixed the Cycles Material Output node.
- Fixed incompatible declaration in getTrimmedCopy_LowLevel method.

### Changed

- Vectorized the Tilt Spline node.
- Instancer node objects are now removed regardless of their numbers of users.
- Return empty spline from Trim Spline node if start and end are equal.

## 2.1.7

### Added

- Added GP Object Input node.
- Added GP Layer Info node.
- Added GP Frame Info node.
- Added GP Stroke Info node.
- Added GP Stroke From Points node.
- Added GP Frame From Strokes node.
- Added GP Layer From Frames node.
- Added GP Object Output node.
- Added Change Spline Direction node.
- Added Transfrom GP Layer node.
- Added Replicate GP Stroke node.
- Added Transform GP Stoke node.
- Added Set GP Layer Attributes node.
- Added Set GP Stroke Attributes node.
- Added GP Material Output node.
- Added GP Object Material Output node.
- Added Replicate GP Layer node.
- Added Offset GP Layer Frames node.
- Added Set Edge Crease node.
- Added Set Polygon Material Index node.
- Added Deep Copy option to the Copy Object Data node.
- Added Decompose Text node.
- Added Object Color Output node.

### Fixed

- Fixed the Splines From Branches algorithm for closed loops.
- Fixed auto execution when the node tree is refreshed during animation.
- Fixed the Distribute Matrices node for the Spiral option.
- Fixed VirtualPyList for singleton lists.
- Fixed error due to duplication of nodes with code effects.
- Fixed unexpected results and crashes during exporting.
- Fixed enum identifiers that had spaces.

### Changed

- Optimized the *Object Instancer* node.
- Make all numeric types comparable.
- Vectorize *Combine Color* node.
- Replace the Font socket pick operator with a *Load Font* operator.
- Moved panels from the Tool region to the UI region.

## 2.1.6

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

## 2.1.5 (0832e2e 7Mar2019 - d3deba4 12Oct2019)

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
- Fixed crash on context view_layer access and *Get Selected Objects* node.
- Fixed *Separate Text Object* node.
- Fixed *Time Code* node.
- Fixed: Fails when trying to rename an object.
- Fixed baking for *Text Object Output* node.
- Fixed the *Offset Vertices* and *Offset Polygons* nodes. Copy the input mesh if needed.
- Fixed crash upon linking to a *Script* node
- Fixed bad precision in the *Wiggle Falloff* node.
- Fixed header alignment for the *Subprograms* menu and the *Remove* nodetree operator.

### Changed

- Redesigned *Execution Triggers* UI.
- Allow multiple comma-separated data paths per *Execution Trigger*.
- Replaced colored icons in the *Node Menu* to be more uniform.
- Started following Blender's class naming conventions.
- Made dependent nodes unsearchable like *Loop Generator* and *Group Output* nodes.
- Changed location of Animation Nodes to Animation Nodes Editor.
- Allow the spline radius to affect the object's scale in the Follow Spline Action.
- Vectorized the *Number Wiggle*, *Euler Wiggle*, and *Quaternion Wiggle* nodes.
- Inform the user that no *Viewport Input* node exists in the *Data Input* panel.

## 2.1.4 (9cfdb0b 16Dec2018 - dd5573b, 7Mar2019)

### Added

- Added new sound system for *Sound* nodes.
- Added *Vectors* output and *Center* options for *Distribute Matrices* node.
- Added *Object Material Output* and *Material Output* nodes.
- Added error handling code when sound files don't exist on disk.
- Added support for packed sounds.
- Added *Viewport Input* node.

### Fixed

- Fixed *toggleObjectVisibilty* function.
- Fixed *Bake To Keyframes* operator.
- Fixed the preferences.
- Fixed *Separate Text Object* node.
- Fixed *Compose Matrix* node.
- Fixed *getSoundData* function, and changed a default value.
- Fixed *Wiggle Action* node.
- Fixed *Mesh Object Input* node.
- Fixed *Vectorized* sockets stop automatic conversion upon duplication #928 #929.
- Fixed *Sort* node.

### Changed

- Add instances to a container collection.
- Automatically unlink objects by calling remove.
- Limit count input in *Vector Wiggle* node.
- Allow access to depsgraph through context.

## 2.1.3 (dfacb9d 8Apr2018 - c41163a 15Dec2018)

### Added

- Added more *troubleshooting info* unsuccessful installation of the addon.
- Added *Combine Mesh* node to the menu.
- Added *Collection Info* node.
- Added *Sort* node.
- Added *Sort* node to the menu.
- Added *BOTTOM_BASELINE* align option in *Text Object Output* node.

### Fixed

- Fixed the node menu.
- Fixed *UV Maps*.
- Fixed *UI Split*.
- Fixed *Spline Normals*.
- Fixed no tabs in the left sidebar (tools panel) anymore.
- Fixed node editor *HUD* position.
- Fixed *Create Auto Execution Trigger* operator.
- Fixed *Transform Vector* node.
- Fixed *Quaternion Math* node.
- Fixed *Quaternion List Combine* node.
- Fixed *Separate Text Object WIP. Poll fails.
- Fixed *Set Vertex Color* node.
- Fixed *Get Selected Objects* node.
- Fixed *Transform Object* node.
- Fixed *Armature Info* node.
- Fixed *Spline Revolve* node.

### Changed

- A new algorithm for *Splines From Edges* node #922.
- *Port Animation Nodes to Blender 2.8* (1c2bbe1 17Oct2018).
- Move *ID* and *Input Data* panels to *UI*.
- Change editor name to *Animation Nodes*.
- Enable error border.
- Removed *Objects From Group* and *Set Layer Visibility* nodes.
- Updated *Object Visibility Input/Output* nodes.
- Removed *Object Group* generic nodes.
- Move *Advanced Node Settings* to *Node* category.

## 2.1.2 (72af0a4 25Mar2018 - 93f1945 8Apr2018)

### Added

- Added *J*, *K* and *M* variables to store current turtle state as a matrix for *L System*.
- Added frame current network operator in the pie menu.

### Fixed

- Fixed sound baking #885, #864.
- Fixed cannot *Evaluate Falloff* with matrices #887.
- Fixed *Separate Text Object* node crash when clicking on update #892.
- Fixed remove unknown sockets from undefined nodes as well #891.

### Changed

## 2.1.1 (7d3153d 17Aug2017 - 2563c53 25Mar2018)

### Added

- Added *Action From Object* node.
- Added *Constant Action* node.
- Added *Wiggle Location Action* node.
- Added *Object Action Output* node.
- Added different modes in *Action Output* node.
- Added *Delay Action* node.
- Added *Follow Spline Action* node.
- Added *Overlay Action* node.
- Added *Normals* and *Tilt* for *Spline*.
- Added *Normals* and *Tilt* for *Poly Spline*.
- Added output *Tilt* attribute in *Evaluate Spline* node.
- Added *Tilt* for spline nodes (*Connect*, *Append Point to Spline*, *Change Spline Type*, *Spline From Points*, *SPline Info*).
- Added new *errorHandlingType* to the nodes.
- Added compilation support for *MAC OS*.
- Added *Noise Falloff* node.
- Added *Action* support in *Offset Matrix* node.
- Added unbounded action support for *Overlay Action* node.
- Added *Chain Action* node.
- Added *Action Viewer* node.
- Added *Mesh Validity* check for mesh object.
- Added *Construct Mesh* node.
- Added *UV Maps* support for mesh object.
- Added *Mesh Info* node.
- Added output mesh object in *Cylinder Mesh* node.
- Added *Circle* node.
- Added *Solidify* node.
- Added custom pivots option in *Transform Polygons* node.
- Added *Transform Mesh* node.
- Added *Evaluate Sound* node in menu.
- Added support for auto insert in *Mesh* and *Vector List*, and *Matrix List* and *Vector List*.
- Added *Polygon* and *Spiral* mode in *Distribute Matrices* node.
- Added *Tilt Spline* and *Mesh From Spline* nodes.
- Added *Cap Ends* option in *Mesh from Spline* node.
- Added initial version of the *L System* node.
- Added partial *L System* generations.
- Added more symbols for *L System*.
- Added presets for *L System*.

### Fixed

- Fixed *Zero Division* in case of *Geometry* nodes.
- Fixed wrong input name of *Project Point On Plane* node.
- Fixed preferences class name for Blender 2.79.
- Fixed *Wiggle Location Action* node.
- Fixed *Spline* trimming.
- Fixed *Bezier Spline* projection.
- Fixed compilation on *Linux* and fast *Noise Wraper*.
- Fixed *Evaluate Falloff* node.
- Fixed *Follow Spline Action* and *Wiggle Action* nodes.
- Fixed *Action From Object* node.
- Fixed spelling in the error message for missing *NumPy*.
- Fixed *Object Transforms Output* node outputs nothing.
- Fixed *Cap Ends* of *Mesh From Spline* node.

### Changed

- Show the file path when there is an error in the file.
- Removed *Scale* and *Translation Matrix* nodes, which are now part of *Compose Matrix* node.
- Replace *Rotation Matrix* node with *Axis Rotation Matrix* node.
- Updated default *conf* to version Blender 2.79.
- Removed *Constant Action* node.
- Joined *Get Spline Samples* node into *Evaluate Spline* node.
- Vectorized the *Vector Angle* node.
- Better handles for straight *Bezier* segments.
- Removed *Barycentric Transform* node.
- Implemented list evaluation for falloffs which roughly *30%* speedup the falloff nodes.
- Improved the *Mesh Input*, *Replicate Mesh*, *Edge to Tube* nodes.
- Changed functionality of the *Transform Polygons* node.
- Removed *Prepare Polygon Transforms* node.
- Speedup *Transform Polygons* node.
- Speedup *Edges of Polygons* node.
- Removed *Separate Mesh Data* node.
- Rendered merge booleans into options in *Circle* node.
- Vectorized *Combine Euler* node.
- Removed *Solidify* Node.
- *Transform Polygons* node supports 3 basis modes.
- Renamed the *Circle* node as *Circle Mesh* node and added in menu.
- Renamed the modes of the *Transform Polygons* node.
- Removed the *Construct Mesh*, *Mesh Data From Object* and *Object Mesh Data* nodes.
- Choose edge based on distance in *Extract Polygons Transforms* node.
- Removed the *Replicate Mesh* node, replaced by *Transform Mesh* node.
- *Mesh* generation nodes should output only a mesh.
- Renamed *Transform Polygons* node to *Offset Polygons* node.
- Speedup the *Circle* and *Spiral* modes of *Distribute Matrices* node.
- Vectorized *Replace Text* node.
- Allowed to skip mesh validation in *Combine Mesh Data* node.

## 2.1.0 (b0e7697 16Jul2017 - 3776c70 17Aug2017)

### Added

- Added the *Unity Triangle* node.
- Implement copy the addon at the specified path the *JSON* file.
- Added *Compose Matrix* node.

### Fixed

- Fixed double frame update.
- Bring back 0.8 transparency for vectorized sockets.
- Fixed *PermissionError* during copying the addon at the specified path.

### Changed

- Raise exception when the folder has a wrong name for addon installation.
- Show degrees instead of radians in *Viewer* node.
- Vectorized the *Separate Euler* node.
- Removed the different frames option from *Object Transforms Output* node.
- Allow *Custom Default* list element when the list is empty.
- Allow lists with different lengths in *Float Math* node.
- Removed *Reference (Basis)* key from *Shape Key* list.
- Cythonized and Vectorized *Line Plane Intersection* node.
- Cythonized and Vectorized *Intersect Line Sphere* node.
- Cythonized aNd Vectorized *Plane Plane Intersection* node.
- Cythonized and Vectorized *Intersect Sphere Plane* node.
- Cythonized and Vectorized *Intersect Sphere Sphere* node.
- Cythonized and Vectorized *Project Point On Line* node.
- Cythonized and Vectorized *Project Point On Plane* node.
