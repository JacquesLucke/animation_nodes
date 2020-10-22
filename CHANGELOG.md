## Unreleased

### Added

- Added *Filter Material List By Name* node.
- Added *Change GP Stroke Direction* node.
- Added create list option to the *Random Quaternion* node.
- Added *Random Boolean* node.
- Added *Random Color* node.
- Added *Find Shortest Path* node.
- Added *Compare Numbers* node.
- Added *Copy Object Modifiers* node.

### Fixed

- Fixed nextBoolean method for XoShiRo256StarStar generators.
- Fixed OpenGL fragment shaders on Core contexts.
- Fixed triangulateMesh method of Mesh.

### Changed

- Vectorized *Mix* nodes.
- *Mix Quaternions* node now uses slerp for mixing
- Vectorized *Convert Angle* node
- Vectorized *Vector Dot Product* node

## 2.2.0 (01 September 2020)

### Added

- Added an option to hide subprogram sockets by default.
- Added default values for Script subprogram inputs.
- Added subtract method to the *Mix Falloff* node.
- Added order weight option for Viewport Input node.
- Added regular polygons mesh generators menu and search entries.
- Added curve dimensions option to the Separate Text node.
- Added matrices output in *Mesh Points Scatter* node.
- Added edges mode in *Mesh Points Scatter* node.
- Added *Vertex Color Fill* attribute to GP strokes.
- Added *Radial Falloff* node.
- Added *Radial* mode to *Object Controller Falloff* node.
- Added *Create Trigger* operator to *Object Controller Falloff* node.
- Added *Extract Matrix Basis* node.
- Added *Normals* output in *Mesh Points Scatter* node.
- Added Interpolation input to *Remap Falloff* node.
- Added *Decompose Text* node to menu.
- Added *Repeat List Elements* node.
- Added Material Indices to Mesh structure.
- Added Material Indices output to *Bmesh Mesh Data* node.
- Added Material Indices input to *Combine Mesh* node.
- Added implicit conversion from Polygon Indices List to Integer List.
- Added *Insert List Element* node.
- Added option to remove Channel in *Wiggle Action* node.
- Added Curvature output to Evaluate Spline node.
- Added Interpolation input to *Float Range* node.
- Added *Mesh Falloff* node.
- Added Object property to BVH Tree socket.

### Fixed

- Fixed the *Make ELement Copies* option in the *Repeat List* node.
- Fixed the *Map Range* node when the input max is less than input min.
- Fixed Sound nodes when scene fps base is not one.

### Changed

- Removed Material Indices input from *Mesh Object Output* node.
- Vectorized *Separate Color* node.
- Vectorized *Separate Quaternion* node.
- Vectorized *Combine Quaternion* node.
- Replaced the inputs of the mesh *Construct BVH Tree* node with a mesh.

# 2.1

## 2.1.8 (08 August 2020)

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
- Added *Calculate Loose Edges* option in *Mesh Object Output* node.
- Added XoShiRo256 random number generators.
- Added mesh *Triangulation* methods and *Triangulate Mesh* node.
- Added Mesh Points Scatter node.
- Added support for 2D vectors in 3D viewer node.

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
- Fixed Grease Pencil nodes for latest Blender API changes.
- Fixed Project Point On Line distance output.
- Fixed missing UV and vertex colors in the Transform Mesh node.
- Fixed bad splines during rendering and baking.
- Fixed the spiral method in the Distribute Matrices node for negative amounts.
- Fixed the output of Set GP Stroke Attributes node for hardness-list input.
- Fixed *Object Action Output* node when action contain bad channels.
- Fixed *Mesh From Spline* node when *Closed Shape* and *Cap Ends* are enabled.
- Fixed wrong sign in scale for matrix list in *Decomposed Matrix* node.
- Fixed bad link conversions between Object and Shape Key sockets.

### Changed

- Vectorized the Tilt Spline node.
- Instancer node objects are now removed regardless of their numbers of users.
- Return empty spline from Trim Spline node if start and end are equal.
- Migrate CI/CD pipeline to Github Workflows.
- Moved Problems panel to UI region.
- Add CI/CD build for Python 3.8 on Linux.
- Rename the *Sort* node as *Sort Numbers* node.

## 2.1.7 (22 February 2020)

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

## 2.1.6 (30 January 2020)

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

## 2.1.5 (12 October 2019)

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
- Fixed header alignment for the *Subprograms* menu and the *Remove* node tree operator.

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

## 2.1.4 (6 March 2019)

### Added

- Added new sound system for *Sound* nodes.
- Added *Vectors* output and *Center* options for *Distribute Matrices* node.
- Added *Object Material Output* and *Material Output* nodes.
- Added error handling code when sound files don't exist on disk.
- Added *Viewport Input* node.

### Fixed

- Fixed *toggleObjectVisibilty* function.
- Fixed *Bake To Keyframes* operator.
- Fixed *Separate Text Object* node.
- Fixed *Compose Matrix* node.
- Fixed *getSoundData* function, and changed a default value.
- Fixed *Wiggle Action* node.
- Fixed *Mesh Object Input* node.
- Fixed *Vectorized* sockets stop automatic conversion upon duplication.
- Fixed *Sort* node.

### Changed

- Add objects to a container collection in *Object Instancer* node.
- Automatically unlink objects by calling remove in *Object Instancer* node.
- Limit count input in *Vector Wiggle* node.

## 2.1.3 (15 December 2018)

### Added

- Added *Spline Per Branche* option to *Splines From Edges* node.
- Added more troubleshooting info upon unsuccessful installation of the add-on.
- Added *Combine Mesh* node to the menu.
- Added *Collection Info* node.
- Added *Sort* node.
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

- Port Animation Nodes to Blender 2.8.
- Move *ID* and *Input Data* panels to *UI* menu.
- Change editor name to *Animation Nodes*.
- Enable error border.
- Removed *Objects From Group* and *Set Layer Visibility* nodes.
- Updated *Object Visibility Input/Output* nodes.
- Removed *Object Group* generic nodes.
- Move *Advanced Node Settings* to *Node* category.
- Refactor 3D viewer node.

## 2.1.2 (8 April 2018)

### Added

- Added *J*, *K* and *M* outputs to *L System* node.
- Added *String* output to *L System* node.
- Added *Frame Current Network* operator in the pie menu.

### Fixed

- Fixed sound baking.
- Fixed *Evaluate Falloff* node with matrices.
- Fixed *Separate Text Object* node crash when clicking on update.

### Changed

- Remove unknown sockets from undefined nodes.

## 2.1.1 (25 March 2018)

### Added

- Added *Action From Object* node.
- Added *Constant Action* node.
- Added *Wiggle Location Action* node.
- Added *Object Action Output* node.
- Added *Delay Action* node.
- Added *Follow Spline Action* node.
- Added *Overlay Action* node.
- Added *Normals* and *Tilt* for *Spline* nodes.
- Added new error handing mechanism for nodes.
- Added compilation support for *MAC OS*.
- Added *Vector Noise* node.
- Added *Noise Falloff* node.
- Added *Action* support in *Offset Matrix* node.
- Added *Chain Action* node.
- Added *Action Viewer* node.
- Added mesh validation checks for mesh nodes.
- Added *UV Maps* support for mesh object.
- Added *Mesh Info* node.
- Added output mesh object in *Cylinder Mesh* node.
- Added *Circle* node.
- Added custom pivot options in *Transform Polygons* node.
- Added *Transform Mesh* node.
- Added *Evaluate Sound* node in menu.
- Added support for auto insert in *Mesh* and *Vector List*, and *Matrix List* and *Vector List*.
- Added *Polygon* and *Spiral* mode in *Distribute Matrices* node.
- Added *Tilt Spline* and *Mesh From Spline* nodes.
- Added *Cap Ends* option in *Mesh from Spline* node.
- Added *L System* node.

### Fixed

- Fixed zero division in case of *Geometry* nodes.
- Fixed wrong input name of *Project Point On Plane* node.
- Fixed preferences class name for Blender 2.79.
- Fixed *Spline* trimming.
- Fixed *Bezier Spline* projection.
- Fixed compilation on *Linux* and fast *Noise Wraper*.
- Fixed *Evaluate Falloff* node.
- Fixed spelling in the error message for missing *NumPy*.
- Fixed *Object Transforms Output* node outputs nothing.

### Changed

- Show the file path when there is an error in the file.
- Removed *Scale* and *Translation Matrix* nodes, which are now part of *Compose Matrix* node.
- Replace *Rotation Matrix* node with *Axis Rotation Matrix* node.
- Updated default *conf.json* file to version Blender 2.79.
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
- Vectorized *Combine Euler* node.
- *Transform Polygons* node supports 3 basis modes.
- Renamed the modes of the *Transform Polygons* node.
- Removed the *Mesh Data From Object* and *Object Mesh Data* nodes.
- Choose edge based on distance in *Extract Polygons Transforms* node.
- Removed the *Replicate Mesh* node, replaced by *Transform Mesh* node.
- Mesh generation nodes now only output a mesh.
- Renamed *Transform Polygons* node to *Offset Polygons* node.
- Vectorized *Replace Text* node.
- Allowed to skip mesh validation in *Combine Mesh Data* node.

## 2.1.0 (17 August 2017)

### Added

- Added the *Unity Triangle* node.
- Added a flag to copy the add-on to the path specified in the `conf.json` file.
- Added *Virtual Lists*.
- Added *Compose Matrix* node.

### Fixed

- Fixed double frame update.
- Fixed *PermissionError* during copying the add-on at the specified path.

### Changed

- Raise exception when the folder has a wrong name for add-on installation.
- Show degrees instead of radians in *Viewer* node.
- Vectorized the *Separate Euler* node.
- Removed the different frame options from *Object Transforms Output* node.
- Allow custom default list element when vectorized list input is empty.
- Allow lists with different lengths in *Float Math* node.
- Removed *Reference (Basis)* key from *Shape Key* list.
- Cythonized and Vectorized *Line Plane Intersection* node.
- Cythonized and Vectorized *Intersect Line Sphere* node.
- Cythonized and Vectorized *Plane Plane Intersection* node.
- Cythonized and Vectorized *Intersect Sphere Plane* node.
- Cythonized and Vectorized *Intersect Sphere Sphere* node.
- Cythonized and Vectorized *Project Point On Line* node.
- Cythonized and Vectorized *Project Point On Plane* node.
- Bring back 0.8 transparency for vectorized sockets.
