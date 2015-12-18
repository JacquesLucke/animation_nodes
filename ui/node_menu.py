import bpy
from bpy.props import *
from .. tree_info import getSubprogramNetworks
from .. utils.nodes import getAnimationNodeTrees

def drawMenu(self, context):
    if context.space_data.tree_type != "an_AnimationNodeTree": return

    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"

    layout.operator("an.node_search", text = "Search", icon = "VIEWZOOM")
    layout.separator()
    layout.menu("an_number_menu", text = "Number", icon = "LINENUMBERS_ON")
    layout.menu("an_vector_menu", text = "Vector", icon = "MAN_TRANS")
    layout.menu("an_rotation_menu", text = "Rotation", icon = "MAN_ROT")
    layout.menu("an_matrix_menu", text = "Matrix", icon = "GRID")
    layout.menu("an_text_menu", text = "Text", icon = "SORTALPHA")
    layout.menu("an_boolean_menu", text = "Boolean", icon = "INLINK")
    layout.menu("an_color_menu", text = "Color", icon = "COLOR")
    layout.menu("an_list_menu", text = "List", icon = "WORDWRAP_ON")
    layout.separator()
    layout.menu("an_object_menu", text = "Object", icon = "OBJECT_DATAMODE")
    layout.menu("an_mesh_menu", text = "Mesh", icon = "MESH_DATA")
    layout.menu("an_spline_menu", text = "Spline", icon = "CURVE_DATA")
    layout.separator()
    layout.menu("an_animation_menu", text = "Animation", icon = "RENDER_ANIMATION")
    layout.menu("an_interpolation_menu", text = "Interpolation", icon = "IPO_BEZIER")
    layout.menu("an_material_menu", text = "Material", icon = "MATERIAL_DATA")
    layout.menu("an_particles_menu", text = "Particles", icon = "PARTICLE_DATA")
    layout.menu("an_fcurve_menu", text = "FCurves", icon = "IPO")
    layout.menu("an_sound_menu", text = "Sound", icon = "SPEAKER")
    layout.menu("an_kdtree_menu", text = "KDTree", icon = "STICKY_UVS_LOC")
    layout.separator()
    layout.menu("an_debug_menu", text = "Debug", icon = "INFO")

    layout.menu("an_subprograms_menu", text = "Subprograms", icon = "FILE_SCRIPT")

def drawNodeTreeChooser(layout, context):
    activeNodeTree = context.space_data.node_tree
    nodeTrees = getAnimationNodeTrees()

    if not activeNodeTree:
        col = layout.column()
        col.scale_y = 1.6
        if len(nodeTrees) == 0:
            col.operator("an.create_node_tree", text = "New Node Tree", icon = "PLUS")
        else:
            for nodeTree in nodeTrees:
                props = col.operator("an.select_node_tree", text = "Select '{}'".format(nodeTree.name), icon = "EYEDROPPER")
                props.nodeTreeName = nodeTree.name

class NumberMenu(bpy.types.Menu):
    bl_idname = "an_number_menu"
    bl_label = "Number Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInputNode", "Integer", {"assignedType" : repr("Integer")})
        insertNode(layout, "an_DataInputNode", "Float", {"assignedType" : repr("Float")})
        insertNode(layout, "an_CreateListNode", "Integer List", {"assignedType" : repr("Integer")})
        insertNode(layout, "an_CreateListNode", "Float List", {"assignedType" : repr("Float")})
        insertNode(layout, "an_FloatRangeListNode", "Integer Range", {"dataType" : repr("Integer")})
        insertNode(layout, "an_FloatRangeListNode", "Float Range", {"dataType" : repr("Float")})
        layout.separator()
        insertNode(layout, "an_RandomNumberNode", "Randomize")
        insertNode(layout, "an_FloatWiggleNode", "Wiggle")
        insertNode(layout, "an_MixDataNode", "Mix", {"dataType" : repr("Float")})
        insertNode(layout, "an_MapRangeNode", "Map Range")
        layout.separator()
        insertNode(layout, "an_FloatClampNode", "Clamp")
        insertNode(layout, "an_ConvertAngleNode", "Convert Angle")
        insertNode(layout, "an_FloatToIntegerNode", "Convert Float To Integer")
        insertNode(layout, "an_RoundNumberNode", "Round")
        insertNode(layout, "an_FloatMathNode", "Math")
        insertNode(layout, "an_ListMathNode", "List Math")

class VectorMenu(bpy.types.Menu):
    bl_idname = "an_vector_menu"
    bl_label = "Vector Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_SeparateVectorNode", "Separate")
        insertNode(layout, "an_CombineVectorNode", "Combine")
        insertNode(layout, "an_VectorFromValueNode", "From Value")
        insertNode(layout, "an_CreateListNode", "List", {"assignedType" : repr("Vector")})
        layout.separator()
        insertNode(layout, "an_RandomVectorNode", "Randomize")
        insertNode(layout, "an_VectorWiggleNode", "Wiggle")
        insertNode(layout, "an_MixDataNode", "Mix", {"dataType" : repr("Vector")})
        layout.separator()
        insertNode(layout, "an_VectorLengthNode", "Length")
        insertNode(layout, "an_VectorDistanceNode", "Distance")
        insertNode(layout, "an_VectorMathNode", "Math")
        insertNode(layout, "an_TransformVectorNode", "Transform Vector")
        insertNode(layout, "an_TransformVectorListNode", "Transform Vector List")

class RotationMenu(bpy.types.Menu):
    bl_idname = "an_rotation_menu"
    bl_label = "Rotation Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DirectionToRotationNode", "Direction to Rotation")
        layout.separator()
        insertNode(layout, "an_CombineEulerNode", "Combine Euler")
        #layout.separator()
        insertNode(layout, "an_ConvertRotationsNode", "Euler to Quaternion", {"conversionType" : repr("EULER_TO_QUATERNION")})
        insertNode(layout, "an_ConvertRotationsNode", "Euler to Matrix", {"conversionType" : repr("EULER_TO_MATRIX")})
        insertNode(layout, "an_ConvertRotationsNode", "Matrix to Euler", {"conversionType" : repr("MATRIX_TO_EULER")})
        layout.separator()
        insertNode(layout, "an_ConvertVectorAndEulerNode", "Euler to Vector", {"conversionType" : repr("EULER_TO_VECTOR")})
        insertNode(layout, "an_ConvertVectorAndEulerNode", "Vector to Euler", {"conversionType" : repr("VECTOR_TO_EULER")})
        layout.separator()
        insertNode(layout, "an_MixDataNode", "Mix Euler", {"dataType" : repr("Euler")})
        layout.separator()
        insertNode(layout, "an_CombineQuaternionNode", "Combine Quaternion")
        #layout.separator()
        insertNode(layout, "an_ConvertRotationsNode", "Quaternion to Euler", {"conversionType" : repr("QUATERNION_TO_EULER")})
        insertNode(layout, "an_ConvertRotationsNode", "Quaternion to Matrix", {"conversionType" : repr("QUATERNION_TO_MATRIX")})
        insertNode(layout, "an_ConvertRotationsNode", "Matrix to Quaternion", {"conversionType" : repr("MATRIX_TO_QUATERNION")})
        layout.separator()
        insertNode(layout, "an_MixDataNode", "Mix Quaternion", {"dataType" : repr("Quaternion")})


class MatrixMenu(bpy.types.Menu):
    bl_idname = "an_matrix_menu"
    bl_label = "Matrix Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DecomposeMatrixNode", "Decompose")
        insertNode(layout, "an_ComposeMatrixNode", "Compose")
        insertNode(layout, "an_CreateListNode", "List", {"assignedType" : repr("Matrix")})
        layout.separator()
        insertNode(layout, "an_TranslationMatrixNode", "Translation")
        insertNode(layout, "an_RotationMatrixNode", "Rotation")
        insertNode(layout, "an_ScaleMatrixNode", "Scale")
        insertNode(layout, "an_MatrixCombineNode", "Combine")
        layout.separator()
        insertNode(layout, "an_MixDataNode", "Mix", {"dataType" : repr("Matrix")})
        insertNode(layout, "an_InvertMatrixNode", "Invert")
        insertNode(layout, "an_MatrixMathNode", "Math")

class TextMenu(bpy.types.Menu):
    bl_idname = "an_text_menu"
    bl_label = "Text Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInputNode", "Input", {"assignedType" : repr("String")})
        insertNode(layout, "an_CreateListNode", "List", {"assignedType" : repr("String")})
        insertNode(layout, "an_RandomStringNode", "Randomize")
        insertNode(layout, "an_CharactersNode", "Characters")
        layout.separator()
        insertNode(layout, "an_SplitTextNode", "Split")
        insertNode(layout, "an_JoinStringsNode", "Join")
        insertNode(layout, "an_TrimTextNode", "Trim")
        layout.separator()
        insertNode(layout, "an_ReplicateStringsNode", "Replicate")
        insertNode(layout, "an_FillStringNode", "Fill")
        insertNode(layout, "an_ReplaceTextNode", "Replace")
        insertNode(layout, "an_StringLengthNode", "Length")
        layout.separator()
        insertNode(layout, "an_TextBlockReaderNode", "Block Reader")
        insertNode(layout, "an_TextBlockWriterNode", "Block Writer")
        layout.separator()
        insertNode(layout, "an_TextSequenceOutputNode", "Sequence Output")
        insertNode(layout, "an_CharacterPropertiesOutputNode", "Character Property")
        insertNode(layout, "an_SeparateTextObjectNode", "Object Separate")
        insertNode(layout, "an_TextObjectOutputNode", "Object Output")

class BooleanMenu(bpy.types.Menu):
    bl_idname = "an_boolean_menu"
    bl_label = "Boolean Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInputNode", "Boolean", {"assignedType" : repr("Boolean")})
        insertNode(layout, "an_InvertNode", "Invert")
        insertNode(layout, "an_CompareNode", "Compare")
        insertNode(layout, "an_LogicOperatorsNode", "Logic")
        insertNode(layout, "an_SwitchNode", "Switch")
        insertNode(layout, "an_BooleanToIntegerNode", "Boolean to Integer")

class ColorMenu(bpy.types.Menu):
    bl_idname = "an_color_menu"
    bl_label = "Color Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ChooseColorNode", "Choose Color")
        insertNode(layout, "an_CombineColorNode", "Combine Color")
        insertNode(layout, "an_SeparateColorNode", "Separate Color")
        insertNode(layout, "an_MixDataNode", "Mix", {"dataType" : repr("Color")})
        insertNode(layout, "an_SetVertexColorNode", "Set Vertex Color")

class ListMenu(bpy.types.Menu):
    bl_idname = "an_list_menu"
    bl_label = "List Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_CreateListNode", "Create")
        insertNode(layout, "an_CombineListsNode", "Combine")
        insertNode(layout, "an_AppendListNode", "Append")
        layout.separator()
        insertNode(layout, "an_GetListElementNode", "Get Element")
        insertNode(layout, "an_SearchListElementNode", "Search")
        insertNode(layout, "an_GetListLengthNode", "Get Length")
        layout.separator()
        insertNode(layout, "an_ShuffleListNode", "Shuffle")
        insertNode(layout, "an_ReverseListNode", "Reverse")
        insertNode(layout, "an_SliceListNode", "Slice")
        insertNode(layout, "an_ShiftListNode", "Shift")

class ObjectMenu(bpy.types.Menu):
    bl_idname = "an_object_menu"
    bl_label = "Object Menu"

    def draw(self, context):
        layout = self.layout

        insertNode(layout, "an_DataInputNode", "Object", {"assignedType" : repr("Object")})
        insertNode(layout, "an_CreateListNode", "List", {"assignedType" : repr("Object")})
        insertNode(layout, "an_GetObjectsFromGroupNode", "From Group")
        layout.separator()
        insertNode(layout, "an_ObjectTransformsInputNode", "Transforms Input")
        insertNode(layout, "an_ObjectTransformsOutputNode", "Transforms Output")
        insertNode(layout, "an_ObjectMatrixInputNode", "Matrix Input")
        insertNode(layout, "an_ObjectMatrixOutputNode", "Matrix Output")
        insertNode(layout, "an_ObjectAttributeInputNode", "Attribute Input")
        insertNode(layout, "an_ObjectAttributeOutputNode", "Attribute Output")
        insertNode(layout, "an_ObjectDataPathOutputNode", "Data Path Output")
        layout.separator()
        insertNode(layout, "an_ObjectVisibilityInputNode", "Visibility Input")
        insertNode(layout, "an_ObjectVisibilityOutputNode", "Visibility Output")
        insertNode(layout, "an_ObjectLayerVisibilityOutputNode", "Layer Visibility Output")
        layout.separator()
        insertNode(layout, "an_ObjectIDKeyNode", "ID Key")
        insertNode(layout, "an_CopyObjectDataNode", "Copy Data")
        insertNode(layout, "an_SetKeyframesNode", "Set Keyframes")
        layout.menu("an_object_utils_menu", text = "Utils")
        layout.separator()
        insertNode(layout, "an_ObjectInstancerNode", "Instancer")

class ObjectUtilsMenu(bpy.types.Menu):
    bl_idname = "an_object_utils_menu"
    bl_label = "Object Utils Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_CreateObjectNode", "Create")
        insertNode(layout, "an_MoveObjectNode", "Move")
        insertNode(layout, "an_TransformObjectNode", "Transform")
        insertNode(layout, "an_UpdateObjectMatricesNode", "Update Matrices")
        insertNode(layout, "an_ResetObjectTransformsNode", "Reset Transformations")
        insertNode(layout, "an_CopyTransformsNode", "Copy Transformations")

class MeshMenu(bpy.types.Menu):
    bl_idname = "an_mesh_menu"
    bl_label = "Mesh Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ObjectMeshDataNode", "Object Mesh Data")
        insertNode(layout, "an_ObjectBoundingBoxNode", "Get Bounding Box")
        insertNode(layout, "an_VertexInfoNode", "Vertex Info")
        insertNode(layout, "an_PolygonInfoNode", "Polygon Info")
        insertNode(layout, "an_TransformPolygonNode", "Transform Polygon")
        layout.separator()
        insertNode(layout, "an_SeparateMeshDataNode", "Separate")
        insertNode(layout, "an_CombineMeshDataNode", "Combine")
        insertNode(layout, "an_MeshDataFromPolygonsNode", "Mesh Data from Polygons")
        layout.menu("an_mesh_generators_menu", text = "Generators")
        layout.menu("an_mesh_operators_menu", text = "Operators")
        layout.separator()
        insertNode(layout, "an_CreateListNode", "Mesh Data List", {"assignedType" : repr("Mesh Data")})
        insertNode(layout, "an_JoinMeshDataList", "Join Mesh Data List")
        insertNode(layout, "an_CreateBMeshFromMeshData", "BMesh from Mesh Data")
        layout.menu("an_mesh_finalizing_menu", text = "Tools")
        layout.separator()
        layout.label("Set On Object:")
        insertNode(layout, "an_SetVerticesOnObjectNode", "  Vertex Locations")
        insertNode(layout, "an_SetMeshDataOnObjectNode", "  Mesh Data")
        insertNode(layout, "an_SetBMeshOnObjectNode", "  BMesh")

class MeshGeneratorsMenu(bpy.types.Menu):
    bl_idname = "an_mesh_generators_menu"
    bl_label = "Mesh Generators Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_LineMeshNode", "Line")
        insertNode(layout, "an_GridMeshNode", "Grid")

class MeshOperatorsMenu(bpy.types.Menu):
    bl_idname = "an_mesh_operators_menu"
    bl_label = "Mesh Operators Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_FindCloseVerticesNode", "Find Close Vertices")
        insertNode(layout, "an_EdgesToPlanesNode", "Edges to Planes")
        layout.separator()
        insertNode(layout, "an_CreateEdgeIndicesNode", "Create Edge Indices")
        insertNode(layout, "an_CreatePolygonIndicesNode", "Create Polygon Indices")
        insertNode(layout, "an_EdgesOfPolygonsNode", "Edges of Polygons")

class MeshFinalizingMenu(bpy.types.Menu):
    bl_idname = "an_mesh_finalizing_menu"
    bl_label = "Mesh Finalizing Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_BMeshRemoveDoublesNode", "Remove Doubles")
        insertNode(layout, "an_BMeshRecalculateFaceNormalsNode", "Recalculate Normals")
        insertNode(layout, "an_ShadeObjectSmoothNode", "Shade Object Smooth")

class SplineMenu(bpy.types.Menu):
    bl_idname = "an_spline_menu"
    bl_label = "Spline Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_SplinesFromObjectNode", "Get from Object")
        insertNode(layout, "an_SplineFromPointsNode", "Create from Points")
        insertNode(layout, "an_SplinesFromEdgesNode", "Create from Edges")
        insertNode(layout, "an_CreateListNode", "List", {"assignedType" : repr("Spline")})
        insertNode(layout, "an_AppendPointToSplineNode", "Append Point")
        layout.separator()
        insertNode(layout, "an_TransformSplineNode", "Transform")
        insertNode(layout, "an_ConnectSplinesNode", "Connect")
        insertNode(layout, "an_TrimSplineNode", "Trim")
        insertNode(layout, "an_MakeSplineCyclicNode", "Make Cyclic")
        insertNode(layout, "an_SmoothBezierSplineNode", "Smooth Bezier")
        layout.separator()
        insertNode(layout, "an_SplineInfoNode", "Info")
        insertNode(layout, "an_EvaluateSplineNode", "Evaluate")
        insertNode(layout, "an_ProjectOnSplineNode", "Project")
        insertNode(layout, "an_GetSplineLengthNode", "Get Length")
        insertNode(layout, "an_GetSplineSamplesNode", "Get Samples")
        layout.separator()
        insertNode(layout, "an_SetSplinesOnObjectNode", "Set on Object")
        insertNode(layout, "an_CurveObjectOutputNode", "Curve Object Output")
        layout.separator()
        insertNode(layout, "an_LoftSplinesNode", "Loft")
        insertNode(layout, "an_RevolveSplineNode", "Revolve")

class AnimationMenu(bpy.types.Menu):
    bl_idname = "an_animation_menu"
    bl_label = "Animation Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_TimeInfoNode", "Time Info")
        insertNode(layout, "an_DelayTimeNode", "Delay")
        insertNode(layout, "an_RepeatTimeNode", "Repeat")
        layout.separator()
        insertNode(layout, "an_AnimateDataNode", "Animate Number", {"dataType" : repr("Float")})
        insertNode(layout, "an_AnimateDataNode", "Animate Vector", {"dataType" : repr("Vector")})
        insertNode(layout, "an_AnimateDataNode", "Animate Euler", {"dataType" : repr("Euler")})
        insertNode(layout, "an_AnimateDataNode", "Animate Quaternion", {"dataType" : repr("Quaternion")})
        insertNode(layout, "an_AnimateDataNode", "Animate Matrix", {"dataType" : repr("Matrix")})
        insertNode(layout, "an_AnimateDataNode", "Animate Color", {"dataType" : repr("Color")})

class InterpolationMenu(bpy.types.Menu):
    bl_idname = "an_interpolation_menu"
    bl_label = "Interpolation Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ConstructInterpolationNode", "Construct")
        insertNode(layout, "an_InterpolationFromCurveMappingNode", "From Curve Mapping")
        insertNode(layout, "an_InterpolationFromFCurveNode", "From FCurve")
        insertNode(layout, "an_EvaluateInterpolationNode", "Evaluate")
        insertNode(layout, "an_MixInterpolationNode", "Mix")

class MaterialMenu(bpy.types.Menu):
    bl_idname = "an_material_menu"
    bl_label = "Material Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_CyclesMaterialOutputNode", "Cycles Material Output")
        insertNode(layout, "an_ViewportColorNode", "Viewport Color")

class ParticlesMenu(bpy.types.Menu):
    bl_idname = "an_particles_menu"
    bl_label = "Particles Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ParticleSystemsInputNode", "Systems Input")
        insertNode(layout, "an_GetParticlesNode", "Get Particles")
        insertNode(layout, "an_ParticlesFromObjectNode", "Particles from Object")
        insertNode(layout, "an_FilterParticlesNode", "State Filter")
        insertNode(layout, "an_ParticleListInfoNode", "Particle List Info")
        insertNode(layout, "an_ParticleInfoNode", "Particle Info")

class FCurveMenu(bpy.types.Menu):
    bl_idname = "an_fcurve_menu"
    bl_label = "FCurve Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_FCurvesFromObjectNode", "From Object")
        insertNode(layout, "an_EvaluateFCurveNode", "Evaluate")
        insertNode(layout, "an_FCurveInfoNode", "Info")
        insertNode(layout, "an_FCurveKeyframesNode", "Keyframes")

class SoundMenu(bpy.types.Menu):
    bl_idname = "an_sound_menu"
    bl_label = "Sound Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_SoundBakeNode", "Bake Sound")
        insertNode(layout, "an_SoundFromSequencesNode", "Sound from Sequences")
        insertNode(layout, "an_GetAllSequencesNode", "Get All Sequences")
        insertNode(layout, "an_SequencesFromChannelNode", "Sequences from Channel")
        insertNode(layout, "an_EvaluateSoundNode", "Evaluate Sound")

class KDTreeMenu(bpy.types.Menu):
    bl_idname = "an_kdtree_menu"
    bl_label = "KDTree Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ConstructKDTreeNode", "Construct")
        insertNode(layout, "an_FindNearestPointInKDTreeNode", "Find Nearest")
        insertNode(layout, "an_FindNearestNPointsInKDTreeNode", "Find Amount")
        insertNode(layout, "an_FindPointsInRadiusInKDTreeNode", "Find in Radius")

class DebugMenu(bpy.types.Menu):
    bl_idname = "an_debug_menu"
    bl_label = "Debug Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DebugNode", "Debug")
        insertNode(layout, "an_DebugLoopNode", "Debug Loop")
        insertNode(layout, "an_DebugListNode", "Debug List")
        insertNode(layout, "an_DebugDrawerNode", "Debug Drawer")
        insertNode(layout, "an_DebugInterpolationNode", "Debug Interpolation")

class SubprogramsMenu(bpy.types.Menu):
    bl_idname = "an_subprograms_menu"
    bl_label = "Subprograms Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_InvokeSubprogramNode", "Invoke Subprogram")
        subprograms = getSubprogramNetworks()
        if len(subprograms) == 0:
            layout.label("   There are no subprograms yet")
        else:
            for network in getSubprogramNetworks():
                insertNode(layout, "an_InvokeSubprogramNode", "-  " + network.name, {"subprogramIdentifier" : repr(network.identifier)})
        layout.separator()
        layout.label("New:")
        insertNode(layout, "an_GroupInputNode", "   Group")
        insertNode(layout, "an_LoopInputNode", "   Loop")
        insertNode(layout, "an_ScriptNode", "   Script")
        layout.separator()
        insertNode(layout, "an_ExpressionNode", "Expression")

def insertNode(layout, type, text, settings = {}, icon = "NONE"):
    operator = layout.operator("node.add_node", text = text, icon = icon)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator

def registerMenu():
    bpy.types.NODE_MT_add.append(drawMenu)

def unregisterMenu():
    bpy.types.NODE_MT_add.remove(drawMenu)
