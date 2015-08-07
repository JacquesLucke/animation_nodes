import bpy
from .. utils.nodes import getAnimationNodeTrees

def drawMenu(self, context):
    if context.space_data.tree_type != "an_AnimationNodeTree": return

    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"

    drawNodeTreeChooser(layout, context)

    layout.operator("an.insert_node", text = "Search", icon = "VIEWZOOM")
    layout.separator()
    layout.menu("an.number_menu", text = "Number")
    layout.menu("an.vector_menu", text = "Vector")
    layout.menu("an.matrix_menu", text = "Matrix")
    layout.menu("an.text_menu", text = "Text")
    layout.menu("an.boolean_menu", text = "Boolean")
    layout.menu("an.color_menu", text = "Color")
    layout.menu("an.list_menu", text = "List")
    layout.separator()
    layout.menu("an.object_menu", text = "Object")
    layout.menu("an.mesh_menu", text = "Mesh")
    layout.menu("an.spline_menu", text = "Spline")
    layout.separator()
    layout.menu("an.sound_menu", text = "Sound")
    layout.menu("an.material_menu", text = "Material")
    layout.menu("an.animation_menu", text = "Animation")
    layout.menu("an.particles_menu", text = "Particles")
    layout.separator()
    layout.menu("an.script_menu", text = "Script")
    layout.menu("an.system_menu", text = "System")

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
    bl_idname = "an.number_menu"
    bl_label = "Number Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInput", "Integer", {"assignedType" : repr("Integer")})
        insertNode(layout, "an_DataInput", "Float", {"assignedType" : repr("Float")})
        insertNode(layout, "an_CreateList", "Integer List", {"assignedType" : repr("Integer")})
        insertNode(layout, "an_CreateList", "Float List", {"assignedType" : repr("Float")})
        insertNode(layout, "an_FloatRangeListNode", "Range")
        layout.separator()
        insertNode(layout, "an_RandomNumberNode", "Randomize")
        insertNode(layout, "an_FloatWiggle", "Wiggle")
        insertNode(layout, "an_BlendDataNode", "Blend", {"dataType" : repr("Float")})
        layout.separator()
        insertNode(layout, "an_FloatClamp", "Clamp")
        insertNode(layout, "an_ConvertAngle", "Convert Angle")
        insertNode(layout, "an_FloatMathNode", "Math")

class VectorMenu(bpy.types.Menu):
    bl_idname = "an.vector_menu"
    bl_label = "Vector Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_SeparateVector", "Separate")
        insertNode(layout, "an_CombineVector", "Combine")
        insertNode(layout, "an_VectorFromValue", "From Value")
        insertNode(layout, "an_CreateList", "List", {"assignedType" : repr("Vector")})
        layout.separator()
        insertNode(layout, "an_RandomVectorNode", "Randomize")
        insertNode(layout, "an_VectorWiggle", "Wiggle")
        insertNode(layout, "an_BlendDataNode", "Blend", {"dataType" : repr("Vector")})
        layout.separator()
        insertNode(layout, "an_VectorLengthNode", "Length")
        insertNode(layout, "an_VectorDistanceNode", "Distance")
        insertNode(layout, "an_VectorMathNode", "Math")
        insertNode(layout, "an_DirectionToRotation", "Direction to Rotation")
        insertNode(layout, "an_TransformVector", "Transform")

class MatrixMenu(bpy.types.Menu):
    bl_idname = "an.matrix_menu"
    bl_label = "Matrix Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DecomposeMatrix", "Decompose")
        insertNode(layout, "an_ComposeMatrix", "Compose")
        insertNode(layout, "an_CreateList", "List", {"assignedType" : repr("Matrix")})
        layout.separator()
        insertNode(layout, "an_TranslationMatrix", "Translation")
        insertNode(layout, "an_RotationMatrix", "Rotation")
        insertNode(layout, "an_ScaleMatrix", "Scale")
        insertNode(layout, "an_MatrixCombine", "Combine")
        layout.separator()
        insertNode(layout, "an_BlendDataNode", "Blend", {"dataType" : repr("Matrix")})
        insertNode(layout, "an_InvertMatrix", "Invert")
        insertNode(layout, "an_MatrixMath", "Math")

class TextMenu(bpy.types.Menu):
    bl_idname = "an.text_menu"
    bl_label = "Text Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInput", "Input", {"assignedType" : repr("String")})
        insertNode(layout, "an_CreateList", "List", {"assignedType" : repr("String")})
        insertNode(layout, "an_RandomStringNode", "Randomize")
        insertNode(layout, "an_CharactersNode", "Characters")
        layout.separator()
        insertNode(layout, "an_SplitText", "Split")
        insertNode(layout, "an_JoinStrings", "Join")
        layout.separator()
        insertNode(layout, "an_ReplicateStringsNode", "Replicate")
        insertNode(layout, "an_TrimText", "Trim")
        insertNode(layout, "an_StringLengthNode", "Length")
        layout.separator()
        insertNode(layout, "an_SeparateTextObject", "Object Separate")
        insertNode(layout, "an_TextBlockReader", "Block Reader")
        insertNode(layout, "an_TextBlockWriter", "Block Writer")
        insertNode(layout, "an_TextSequenceOutput", "Sequence Output")
        insertNode(layout, "an_TextOutputNode", "Object Output")

class BooleanMenu(bpy.types.Menu):
    bl_idname = "an.boolean_menu"
    bl_label = "Boolean Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInput", "Boolean", {"assignedType" : repr("Boolean")})
        insertNode(layout, "an_InvertNode", "Invert")
        insertNode(layout, "an_CompareNode", "Compare")
        insertNode(layout, "an_SwitchNode", "Switch")

class ColorMenu(bpy.types.Menu):
    bl_idname = "an.color_menu"
    bl_label = "Color Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ColorInputNode", "RGB")
        insertNode(layout, "an_CombineColor", "Combine RGBA")
        insertNode(layout, "an_ColorMix", "Mix")
        insertNode(layout, "an_SetVertexColor", "Set Vertex Color")

class ListMenu(bpy.types.Menu):
    bl_idname = "an.list_menu"
    bl_label = "List Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_CreateList", "Create")
        insertNode(layout, "an_combine_lists_node", "Combine")
        insertNode(layout, "an_AppendListNode", "Append")
        layout.separator()
        insertNode(layout, "an_GetListElementNode", "Get Element")
        insertNode(layout, "an_GetListLengthNode", "Get Length")
        layout.separator()
        insertNode(layout, "an_ShuffleListNode", "Shuffle")
        insertNode(layout, "an_ReverseListNode", "Reverse")


class ObjectMenu(bpy.types.Menu):
    bl_idname = "an.object_menu"
    bl_label = "Object Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_DataInput", "Input", {"assignedType" : repr("Object")})
        insertNode(layout, "an_CreateList", "List", {"assignedType" : repr("Object")})
        insertNode(layout, "an_ObjectGroupInput", "Group Input")
        layout.separator()
        insertNode(layout, "an_ObjectTransformsInput", "Transforms Input")
        insertNode(layout, "an_ObjectTransformsOutput", "Transforms Output")
        insertNode(layout, "an_ObjectMatrixInput", "Matrix Input")
        insertNode(layout, "an_ObjectMatrixOutputNode", "Matrix Output")
        insertNode(layout, "an_ObjectAttributeInputNode", "Attribute Input")
        insertNode(layout, "an_ObjectAttributeOutputNode", "Attribute Output")
        layout.separator()
        insertNode(layout, "an_ObjectIDKey", "ID Key")
        insertNode(layout, "an_CopyObjectData", "Copy Data")
        insertNode(layout, "an_CopyTransformsNode", "Copy Transforms")
        layout.separator()
        insertNode(layout, "an_ObjectInstancer", "Instancer")

class MeshMenu(bpy.types.Menu):
    bl_idname = "an.mesh_menu"
    bl_label = "Mesh Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ObjectMeshInfo", "Data Info")
        insertNode(layout, "an_SeparateMeshData", "Separate")
        insertNode(layout, "an_CombineMeshData", "Combine")
        insertNode(layout, "an_AppendToMeshData", "Append")
        layout.menu("an.mesh_operators_menu", text = "Operators")
        layout.separator()
        insertNode(layout, "an_CreateMeshFromData", "Create from Data")
        insertNode(layout, "an_SetMeshOnObject", "Set on Object")
        layout.menu("an.mesh_finalizing_menu", text = "Tools")
        layout.separator()
        insertNode(layout, "an_VertexInfo", "Vertex Info")
        insertNode(layout, "an_PolygonInfo", "Polygon Info")
        insertNode(layout, "an_TransformVertex", "Transform Vertex")
        insertNode(layout, "an_TransformPolygon", "Transform Polygon")

class MeshOperatorsMenu(bpy.types.Menu):
    bl_idname = "an.mesh_operators_menu"
    bl_label = "Mesh Operators Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_FindCloseVertices", "Find Close Vertices")
        insertNode(layout, "an_EdgesToPlanes", "Edges to Planes")

class MeshFinalizingMenu(bpy.types.Menu):
    bl_idname = "an.mesh_finalizing_menu"
    bl_label = "Mesh Finalizing Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_MeshRemoveDoubles", "Remove Doubles")
        insertNode(layout, "an_MeshRecalculateFaceNormals", "Recalculate Normals")
        insertNode(layout, "an_MakeObjectSmooth", "Smooth Object")

class SplineMenu(bpy.types.Menu):
    bl_idname = "an.spline_menu"
    bl_label = "Spline Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_SplinesFromObject", "Get from Object")
        insertNode(layout, "an_CreateSpline", "Create from Points")
        insertNode(layout, "an_CreateList", "List", {"assignedType" : repr("Spline")})
        insertNode(layout, "an_AppendPointToSpline", "Append Point")
        insertNode(layout, "an_SmoothBezierSpline", "Smooth Bezier")
        insertNode(layout, "an_MakeSplineCyclic", "Make Cyclic")
        insertNode(layout, "an_TrimSpline", "Trim")
        insertNode(layout, "an_TransformSpline", "Transform")
        insertNode(layout, "an_SetSplinesOnObject", "Set on Object")
        insertNode(layout, "an_CurveProperties", "Set Curve Properties")
        layout.separator()
        insertNode(layout, "an_SplineInfo", "Info")
        insertNode(layout, "an_EvaluateSpline", "Evaluate")
        insertNode(layout, "an_ProjectOnSpline", "Project")
        insertNode(layout, "an_GetSplineLength", "Get Length")
        insertNode(layout, "an_GetSplineSamples", "Get Samples")
        layout.separator()
        insertNode(layout, "an_LoftSplines", "Loft")
        insertNode(layout, "an_RevolveSpline", "Revolve")

class SoundMenu(bpy.types.Menu):
    bl_idname = "an.sound_menu"
    bl_label = "Sound Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_SequencerSoundInput", "Sequencer Sound Input")

class MaterialMenu(bpy.types.Menu):
    bl_idname = "an.material_menu"
    bl_label = "Material Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_CyclesMaterialOutputNode", "Cycles Material Output")
        insertNode(layout, "an_ViewportColorNode", "Viewport Color")

class AnimationMenu(bpy.types.Menu):
    bl_idname = "an.animation_menu"
    bl_label = "Animation Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_TimeInfoNode", "Time Info")
        insertNode(layout, "an_SetKeyframesNode", "Set Keyframes")
        layout.separator()
        insertNode(layout, "an_InterpolationNode", "Interpolation")
        insertNode(layout, "an_EvaluateInterpolation", "Evaluate Interpolation")
        insertNode(layout, "an_MixInterpolation", "Mix Interpolations")

class ParticlesMenu(bpy.types.Menu):
    bl_idname = "an.particles_menu"
    bl_label = "Particles Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ParticleSystemsInput", "Systems Input")
        insertNode(layout, "an_GetParticles", "Get Particles")
        insertNode(layout, "an_FilterParticles", "State Filter")
        insertNode(layout, "an_ParticlesInfo", "Particle List Info")
        insertNode(layout, "an_ParticleInfo", "Particle Info")

class ScriptMenu(bpy.types.Menu):
    bl_idname = "an.script_menu"
    bl_label = "Script Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ExpressionNode", "Expression")
        insertNode(layout, "an_ScriptNode", "Script")
        insertNode(layout, "an_ScriptNode", "Script from Clipboard", {"makeFromClipboard" : repr(True) })

class SystemMenu(bpy.types.Menu):
    bl_idname = "an.system_menu"
    bl_label = "System Menu"

    def draw(self, context):
        layout = self.layout
        insertNode(layout, "an_ConvertNode", "Convert")
        insertNode(layout, "an_DebugOutputNode", "Debug")



def insertNode(layout, type, text, settings = {}):
    operator = layout.operator("node.add_node", text = text)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator


class CreateNodeTree(bpy.types.Operator):
    bl_idname = "an.create_node_tree"
    bl_label = "Create Node Tree"
    bl_description = "Create a new Animation Node tree"
    bl_options = {"REGISTER"}

    def execute(self, context):
        nodeTree = bpy.data.node_groups.new(name = "NodeTree", type = "an_AnimationNodeTree")
        context.space_data.node_tree = nodeTree
        context.area.tag_redraw()
        return {"FINISHED"}


class SelectNodeTree(bpy.types.Operator):
    bl_idname = "an.select_node_tree"
    bl_label = "Select Node Tree"
    bl_description = "Select a Animation Node tree"
    bl_options = {"REGISTER"}

    nodeTreeName = bpy.props.StringProperty(default = "")

    def execute(self, context):
        nodeTree = bpy.data.node_groups.get(self.nodeTreeName)
        context.space_data.node_tree = nodeTree
        context.area.tag_redraw()
        return {"FINISHED"}


def registerMenu():
    bpy.types.NODE_MT_add.append(drawMenu)

def unregisterMenu():
    bpy.types.NODE_MT_add.remove(drawMenu)
