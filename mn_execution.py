import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *
from mn_cache import clearExecutionCache
from mn_network_code_generator import getAllNetworkCodeStrings

ALLOW_COMPILING = True

compiledCodeObjects = []
codeStrings = []

def updateAnimationTrees(treeChanged = True):
	if ALLOW_COMPILING:
		forbidCompiling()
		start = time.clock()
		if treeChanged:
			rebuildNodeNetworks()
		for i, codeObject in enumerate(compiledCodeObjects):
			if bpy.context.scene.showFullError: 
				exec(codeObject, {})
			else:
				try: exec(codeObject, {})
				except BaseException as e:
					rebuildNodeNetworks()
					try: exec(codeObject, {})
					except BaseException as e: print(e)
		clearExecutionCache()
		if bpy.context.scene.printUpdateTime:
			timeSpan = time.clock() - start
			print("Exec. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
		allowCompiling()
			
def allowCompiling():
	global ALLOW_COMPILING
	ALLOW_COMPILING = True
def forbidCompiling():
	global ALLOW_COMPILING
	ALLOW_COMPILING = False
			
			
# compile code objects
################################

def rebuildNodeNetworks():
	global compiledCodeObjects, codeStrings
	del compiledCodeObjects[:]
	del codeStrings[:]
	try:
		codeStrings = getAllNetworkCodeStrings()
		for code in codeStrings:
			compiledCodeObjects.append(compile(code, "<string>", "exec"))
	except:
		pass
				
		
# Force Cache Rebuilding Panel
##############################
		
class AnimationNodesPanel(bpy.types.Panel):
	bl_idname = "mn.panel"
	bl_label = "Animation Nodes"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout
		layout.operator("mn.force_full_update")
		layout.operator("mn.print_node_tree_execution_string")
		scene = context.scene
		layout.label("Update when:")
		layout.prop(scene, "updateAnimationTreeOnFrameChange", text = "Frames Changes")
		layout.prop(scene, "updateAnimationTreeOnSceneUpdate", text = "Scene Updates")
		layout.prop(scene, "updateAnimationTreeOnPropertyChange", text = "Property Changes")
		layout.prop(scene, "printUpdateTime", text = "Print Update Time")
		layout.prop(scene, "showFullError", text = "Show Full Error")
		layout.prop(scene, "nodeExecutionProfiling", text = "Node Execution Profiling")
		
		layout.prop(scene, "customNodeName")
		newNode = layout.operator("node.add_node")
		newNode.use_transform = True
		newNode.type = scene.customNodeName
		layout.operator("mn.load_normal_node_template")
		layout.operator("mn.append_auto_update_code")
		
		
		
class ForceNodeTreeUpdate(bpy.types.Operator):
	bl_idname = "mn.force_full_update"
	bl_label = "Force Node Tree Update"

	def execute(self, context):
		updateAnimationTrees(treeChanged = True)
		return {'FINISHED'}
		
class PrintNodeTreeExecutionStrings(bpy.types.Operator):
	bl_idname = "mn.print_node_tree_execution_string"
	bl_label = "Print Node Tree Code"

	def execute(self, context):
		print()
		for codeString in codeStrings:
			print(codeString)
			print()
			print("-"*80)
			print()
		return {'FINISHED'}
		
class LoadNormalNodeTemplate(bpy.types.Operator):
	bl_idname = "mn.load_normal_node_template"
	bl_label = "Load Normal Node Template"

	def execute(self, context):
		from mn_node_template import getNormalNodeTemplate, getAutoRegisterCode
		textBlockName = "mn_node_template.py"
		textBlock = bpy.data.texts.get(textBlockName)
		if textBlock is None:
			textBlock = bpy.data.texts.new(textBlockName)
		textBlock.clear()
		textBlock.write(getNormalNodeTemplate())
		textBlock.write(getAutoRegisterCode())
		return {'FINISHED'}
		
class AppendAutoUpdateCode(bpy.types.Operator):
	bl_idname = "mn.append_auto_update_code"
	bl_label = "Append Auto Update Code"

	def execute(self, context):
		from mn_node_template import getAutoRegisterCode
		for area in bpy.context.screen.areas:
			for space in area.spaces:
				if space.type == "TEXT_EDITOR":
					if space.text is not None:
						textString = space.text.as_string()
						textString += getAutoRegisterCode()
						space.text.from_string(textString)
		return {'FINISHED'}
		
# class CustomNodeMenu(bpy.types.Menu):
	# bl_idname = "mn.node_menu"
	# bl_label = "Animation Nodes"
	
	# def draw(self, context):
		# layout = self.layout
		# addNode = layout.operator("node.add_node")
		# addNode.type = "mn_TimeInfoNode"
		# addNode.use_transform = True
		
def menuDraw(self, context):
	layout = self.layout
	addNode = layout.operator("node.add_node")
	addNode.type = "mn_TimeInfoNode"
	addNode.use_transform = True
bpy.types.NODE_MT_add.append(menuDraw)
	
	
		
# handlers to start the update
##############################

bpy.types.Scene.updateAnimationTreeOnFrameChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Frame Change")
bpy.types.Scene.updateAnimationTreeOnSceneUpdate = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Scene Update")
bpy.types.Scene.updateAnimationTreeOnPropertyChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Property Change")

bpy.types.Scene.printUpdateTime = bpy.props.BoolProperty(default = False, name = "Print Update Time")
bpy.types.Scene.showFullError = bpy.props.BoolProperty(default = False, name = "Show Full Error")
bpy.types.Scene.nodeExecutionProfiling = bpy.props.BoolProperty(default = False, name = "Node Execution Profiling")

def getCustomNodes(self, context):
	from mn_node_base import AnimationNode
	from mn_node_register import getAllNodeIdNames
	officialNodeNames = getAllNodeIdNames()
	allNodeTypes = bpy.types.Node.__subclasses__()
	customNodeNames = []
	for nodeType in allNodeTypes:
		if hasattr(nodeType, "bl_idname") and issubclass(nodeType, AnimationNode):
			if nodeType.bl_idname not in officialNodeNames:
				customNodeNames.append(nodeType.bl_idname)
	customNodeNames = list(set(customNodeNames))
	customNodeItems = []
	for customNodeName in customNodeNames:
		customNodeItems.append((customNodeName, customNodeName, ""))
	return customNodeItems
	
bpy.types.Scene.customNodeName = bpy.props.EnumProperty(items = getCustomNodes, name = "Custom Node Name")
	
@persistent
def frameChangeHandler(scene):
	if scene.updateAnimationTreeOnFrameChange:
		updateAnimationTrees(False)
@persistent
def sceneUpdateHandler(scene):
	if scene.updateAnimationTreeOnSceneUpdate:
		updateAnimationTrees(False)
@persistent
def fileLoadHandler(scene):
	updateAnimationTrees(True)
def nodePropertyChanged(self, context):
	if context.scene.updateAnimationTreeOnPropertyChange:
		updateAnimationTrees(False)
def nodeTreeChanged():
	updateAnimationTrees(True)

	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)