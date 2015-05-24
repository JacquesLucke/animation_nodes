import bpy
from . utils.mn_node_utils import getAnimationNodeTrees
        
def drawMenu(self, context):
    if context.space_data.tree_type != "mn_AnimationNodeTree": return
    
    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    
    drawNodeTreeChooser(layout, context)    
    
    layout.operator("mn.insert_node", text = "Search", icon = "VIEWZOOM")
    layout.separator()
    layout.menu("mn.number_menu", text = "Number")
    layout.menu("mn.vector_menu", text = "Vector")
    layout.menu("mn.matrix_menu", text = "Matrix")
    layout.menu("mn.text_menu", text = "Text")
    layout.menu("mn.boolean_menu", text = "Boolean")
    layout.menu("mn.color_menu", text = "Color")
    layout.menu("mn.list_menu", text = "List")
    layout.separator()
    layout.menu("mn.object_menu", text = "Object")
    layout.menu("mn.mesh_menu", text = "Mesh")
    layout.menu("mn.spline_menu", text = "Spline")
    layout.separator()
    layout.menu("mn.sound_menu", text = "Sound")
    layout.menu("mn.material_menu", text = "Material")
    layout.menu("mn.animation_menu", text = "Animation")
    layout.menu("mn.particles_menu", text = "Particles")
    layout.separator()
    layout.menu("mn.script_menu", text = "Script")
    layout.menu("mn.debug_menu", text = "Debug")
    layout.menu("mn.system_menu", text = "System") 

def drawNodeTreeChooser(layout, context):
    activeNodeTree = context.space_data.node_tree
    nodeTrees = getAnimationNodeTrees()
    
    if not activeNodeTree:
        col = layout.column()
        col.scale_y = 1.6
        if len(nodeTrees) == 0:
            col.operator("mn.create_node_tree", text = "New Node Tree", icon = "PLUS")
        else:
            for nodeTree in nodeTrees:
                props = col.operator("mn.select_node_tree", text = "Select '{}'".format(nodeTree.name), icon = "EYEDROPPER")
                props.nodeTreeName = nodeTree.name    
    
        
class NumberMenu(bpy.types.Menu):
    bl_idname = "mn.number_menu"
    bl_label = "Number Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_IntegerInputNode", "Integer")
        insertNode(layout, "mn_FloatInputNode", "Float")
        insertNode(layout, "mn_FloatListInputNode", "Float List")
        insertNode(layout, "mn_RandomNumberNode", "Random")
        insertNode(layout, "mn_FloatWiggle", "Wiggle")
        insertNode(layout, "mn_AnimateFloatNode", "Animate")
        insertNode(layout, "mn_FloatClamp", "Clamp")
        insertNode(layout, "mn_FloatMathNode", "Math")
        
class VectorMenu(bpy.types.Menu):
    bl_idname = "mn.vector_menu"
    bl_label = "Vector Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_CombineVector", "Combine")       
        insertNode(layout, "mn_SeparateVector", "Separate")       
        insertNode(layout, "mn_RandomVectorNode", "Random")       
        insertNode(layout, "mn_VectorWiggle", "Wiggle")       
        insertNode(layout, "mn_AnimateVectorNode", "Animate")       
        insertNode(layout, "mn_VectorLengthNode", "Length")       
        insertNode(layout, "mn_VectorDistanceNode", "Distance")       
        insertNode(layout, "mn_TransfromVector", "Transform")       
        insertNode(layout, "mn_VectorMathNode", "Math")       
        insertNode(layout, "mn_VectorFromValue", "From Value")       
        insertNode(layout, "mn_DirectionToRotation", "Direction to Rotation")       
                
class MatrixMenu(bpy.types.Menu):
    bl_idname = "mn.matrix_menu"
    bl_label = "Matrix Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_TranslationMatrix", "Translation")                       
        insertNode(layout, "mn_RotationMatrix", "Rotation")                       
        insertNode(layout, "mn_ScaleMatrix", "Scale")
        insertNode(layout, "mn_MatrixCombine", "Combine")                     
        layout.separator()
        insertNode(layout, "mn_ComposeMatrix", "Compose")                       
        insertNode(layout, "mn_DecomposeMatrix", "Decompose")                     
        insertNode(layout, "mn_AnimateMatrixNode", "Animate")                     
        insertNode(layout, "mn_InvertMatrix", "Invert")                     
        insertNode(layout, "mn_MatrixMath", "Math")                     
                
class TextMenu(bpy.types.Menu):
    bl_idname = "mn.text_menu"
    bl_label = "Text Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_StringInputNode", "Text")                   
        insertNode(layout, "mn_StringListInputNode", "Text List")                   
        insertNode(layout, "mn_RandomStringNode", "Random")  
        insertNode(layout, "mn_CharactersNode", "Characters")                   
        insertNode(layout, "mn_SplitText", "Split")                   
        insertNode(layout, "mn_CombineStringsNode", "Combine")                   
        insertNode(layout, "mn_ReplicateStringsNode", "Replicate")                   
        insertNode(layout, "mn_SubstringNode", "Trim Text")                   
        insertNode(layout, "mn_StringAnalyzeNode", "Analyze Text")   
        insertNode(layout, "mn_TextBlockReader", "Text Block Reader")                     
        insertNode(layout, "mn_TextBlockWriter", "Text Block Writer") 
        insertNode(layout, "mn_SeparateTextObject", "Separate Text Object")                
        insertNode(layout, "mn_TextOutputNode", "Text Object Output")   
        
class BooleanMenu(bpy.types.Menu):
    bl_idname = "mn.boolean_menu"
    bl_label = "Boolean Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_BooleanInputNode", "Boolean")                         
        insertNode(layout, "mn_InvertNode", "Invert")                         
        insertNode(layout, "mn_CompareNode", "Compare")                         
        insertNode(layout, "mn_ConditionNode", "Condition") 

class ColorMenu(bpy.types.Menu):
    bl_idname = "mn.color_menu"
    bl_label = "Color Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_ColorInputNode", "RGB")                                   
        insertNode(layout, "mn_CombineColor", "Combine RGBA")                                   
        insertNode(layout, "mn_ColorMix", "Mix")                  
        insertNode(layout, "mn_SetVertexColor", "Set Vertex Color")         
        
class ListMenu(bpy.types.Menu):
    bl_idname = "mn.list_menu"
    bl_label = "List Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_GetListElementNode", "Get Element")             
        insertNode(layout, "mn_SetListElementNode", "Set Element")             
        insertNode(layout, "mn_GetListLengthNode", "Length")              
        insertNode(layout, "mn_CombineListsNode", "Combine Lists")             
        insertNode(layout, "mn_AppendListNode", "Append to List")             
        insertNode(layout, "mn_ShuffleListNode", "Shuffle")             
        insertNode(layout, "mn_ReverseListNode", "Reverse")             
        
class ObjectMenu(bpy.types.Menu):
    bl_idname = "mn.object_menu"
    bl_label = "Object Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_ObjectInputNode", "Object")                            
        insertNode(layout, "mn_ObjectListInputNode", "Object List")                            
        insertNode(layout, "mn_ObjectGroupInput", "Object Group")                     
        insertNode(layout, "mn_ObjectInfoNode", "Transforms Input") 
        insertNode(layout, "mn_ObjectTransformsOutput", "Transforms Output")                             
        insertNode(layout, "mn_ObjectMatrixInput", "Matrix input")   
        insertNode(layout, "mn_ObjectMatrixOutputNode", "Matrix Output")  
        insertNode(layout, "mn_ObjectAttributeInputNode", "Attribute Input")                            
        insertNode(layout, "mn_ObjectAttributeOutputNode", "Attribute Output")                           
        insertNode(layout, "mn_ObjectKeyframeInput", "AN Keyframe")                            
        insertNode(layout, "mn_CopyObjectData", "Copy Data")  
        insertNode(layout, "mn_CopyTransformsNode", "Copy Transforms")                            
        insertNode(layout, "mn_ObjectInstancer", "Instancer") 
        
class MeshMenu(bpy.types.Menu):
    bl_idname = "mn.mesh_menu"
    bl_label = "Mesh Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_ObjectMeshInfo", "Mesh Info")    
        insertNode(layout, "mn_SeparateMeshData", "Separate Mesh Data")                                     
        insertNode(layout, "mn_CombineMeshData", "Combine Mesh Data") 
        insertNode(layout, "mn_AppendToMeshData", "Append to Mesh Data")
        layout.menu("mn.mesh_operators_menu", text = "Mesh Operators")
        layout.separator()                                    
        insertNode(layout, "mn_CreateMeshFromData", "Mesh from Data")                                   
        insertNode(layout, "mn_SetMeshOnObject", "Set Mesh on Object")
        layout.menu("mn.mesh_finalizing_menu", text = "Mesh Finalizing")
        layout.separator()                                  
        insertNode(layout, "mn_VertexInfo", "Vertex Info")                                     
        insertNode(layout, "mn_PolygonInfo", "Polygon Info")                                     
        insertNode(layout, "mn_TransformVertex", "Transform Vertex")                                     
        insertNode(layout, "mn_TransformPolygon", "Transform Polygon") 
        
class MeshOperatorsMenu(bpy.types.Menu):
    bl_idname = "mn.mesh_operators_menu"
    bl_label = "Mesh Operators Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_FindCloseVertices", "Find Close Vertices")         
        insertNode(layout, "mn_EdgesToPlanes", "Edges to Planes")      

class MeshFinalizingMenu(bpy.types.Menu):
    bl_idname = "mn.mesh_finalizing_menu"
    bl_label = "Mesh Finalizing Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_MeshRemoveDoubles", "Remove Doubles")         
        insertNode(layout, "mn_MeshRecalculateFaceNormals", "Recalculate Normals")         
        insertNode(layout, "mn_MakeObjectSmooth", "Smooth Object")         
        
class SplineMenu(bpy.types.Menu):
    bl_idname = "mn.spline_menu"
    bl_label = "Spline Menu"
    
    def draw(self, context):
        layout = self.layout                                             
        insertNode(layout, "mn_SplineEvaluator", "Evaluate")                                                 
        insertNode(layout, "mn_ProjectOnSpline", "Project")
        insertNode(layout, "mn_CreateSpline", "Create Spline")
        insertNode(layout, "mn_SplinesFromObject", "Splines from Object")
        insertNode(layout, "mn_SetSplinesOnObject", "Set Splines on Object")
        layout.separator()
        insertNode(layout, "mn_LoftSplines", "Loft")
        insertNode(layout, "mn_RevolveSpline", "Revolve")
                                  
class SoundMenu(bpy.types.Menu):
    bl_idname = "mn.sound_menu"
    bl_label = "Sound Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_SoundBakeNode", "Bake")                                   
        insertNode(layout, "mn_SoundBakeReaderNode", "Baked Sound Reader")                                   
        insertNode(layout, "mn_SoundBakeInput", "Bake Input")                                                    
                
class MaterialMenu(bpy.types.Menu):
    bl_idname = "mn.material_menu"
    bl_label = "Material Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_CyclesMaterialOutputNode", "Cycles Material Output")                
        insertNode(layout, "mn_ViewportColorNode", "Viewport Color")                
                
class AnimationMenu(bpy.types.Menu):
    bl_idname = "mn.animation_menu"
    bl_label = "Animation Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_TimeInfoNode", "Time Info")     
        insertNode(layout, "mn_SetKeyframesNode", "Set Keyframes")    
        layout.separator() 
        insertNode(layout, "mn_InterpolationNode", "Interpolation")     
        insertNode(layout, "mn_EvaluateInterpolation", "Evaluate Interpolation")     
        insertNode(layout, "mn_MixInterpolation", "Mix Interpolations")   
        
class ParticlesMenu(bpy.types.Menu):
    bl_idname = "mn.particles_menu"
    bl_label = "Particles Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_ParticleSystemsInput", "Particle Systems Input")              
        insertNode(layout, "mn_ParticleSystemInfo", "Particle Systems Info")              
        insertNode(layout, "mn_FilterParticles", "Filter Particles")              
        insertNode(layout, "mn_ParticlesInfo", "Particles Info")              
        insertNode(layout, "mn_ParticleInfo", "Particle Info")              
        
class ScriptMenu(bpy.types.Menu):
    bl_idname = "mn.script_menu"
    bl_label = "Script Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_ExpressionNode", "Expression")           
        insertNode(layout, "mn_ScriptNode", "Script")           
        insertNode(layout, "mn_ScriptNode", "Script from Clipboard", {"makeFromClipboard" : repr(True) })
        
class DebugMenu(bpy.types.Menu):
    bl_idname = "mn.debug_menu"
    bl_label = "Debug Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_DebugOutputNode", "Generic Socket")          
        insertNode(layout, "mn_DebugVectorOutputNode", "Vector Socket")          
        
class SystemMenu(bpy.types.Menu):
    bl_idname = "mn.system_menu"
    bl_label = "System Menu"
    
    def draw(self, context):
        layout = self.layout
        insertNode(layout, "mn_LoopCallerNode", "Loop") 
        insertNode(layout, "mn_GroupCaller", "Group Caller") 
        insertNode(layout, "mn_GroupInput", "Group Input") 
        insertNode(layout, "mn_GroupOutput", "Group Output") 
        layout.separator()
        insertNode(layout, "mn_NetworkUpdateSettingsNode", "Update Settings") 
                
                
                
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
    bl_idname = "mn.create_node_tree"
    bl_label = "Create Node Tree"
    bl_description = "Create a new Animation Node tree"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        nodeTree = bpy.data.node_groups.new(name = "NodeTree", type = "mn_AnimationNodeTree")
        context.space_data.node_tree = nodeTree
        context.area.tag_redraw()
        return {"FINISHED"}

        
class SelectNodeTree(bpy.types.Operator):
    bl_idname = "mn.select_node_tree"
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