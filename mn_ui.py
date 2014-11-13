import bpy
from mn_execution import getCodeStrings, resetCompileBlocker, updateAnimationTrees
from mn_keyframes import *
from mn_utils import *

class AnimationNodesPerformance(bpy.types.Panel):
	bl_idname = "mn.performance_panel"
	bl_label = "Performance"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Settings"
	
	@classmethod
	def poll(self, context):
		return context.space_data.tree_type == "AnimationNodeTreeType"
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.prop(scene.mn_settings.update, "frameChange", text = "Frames Update")
		layout.prop(scene.mn_settings.update, "sceneUpdate", text = "Scene Update")
		layout.prop(scene.mn_settings.update, "propertyChange", text = "Property Update")
		layout.prop(scene.mn_settings.update, "skipFramesAmount")
	
class CustomAnimationNodes(bpy.types.Panel):
	bl_idname = "mn.custom_nodes_panel"
	bl_label = "Custom Nodes"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Settings"
	
	@classmethod
	def poll(self, context):
		return context.space_data.tree_type == "AnimationNodeTreeType"
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.prop(scene, "customNodeCategory", text = "Category")
		customNodeClasses = getCustomNodesInCategory(scene.customNodeCategory)
		for nodeClass in customNodeClasses:
			newNode = layout.operator("node.add_node", text = nodeClass.bl_label)
			newNode.type = nodeClass.bl_idname
			newNode.use_transform = True
	
class AnimationNodesDeveloperPanel(bpy.types.Panel):
	bl_idname = "mn.developer_panel"
	bl_label = "Developer"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Settings"
	
	@classmethod
	def poll(self, context):
		return context.space_data.tree_type == "AnimationNodeTreeType"
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		col = layout.column(align = True)
		col.operator("mn.load_normal_node_template", "Load Template")
		col.operator("mn.append_auto_update_code")
		
		col = layout.column(align = True)
		col.operator("mn.force_full_update")
		col.operator("mn.print_node_tree_execution_string")
		
		col = layout.column(align = True)
		col.prop(scene.mn_settings.developer, "printUpdateTime", text = "Print Update Time")
		col.prop(scene.mn_settings.developer, "printGenerationTime", text = "Print Generation Time")
		col.prop(scene.mn_settings.developer, "showErrors", text = "Show Errors")
		col.prop(scene.mn_settings.developer, "executionProfiling", text = "Node Execution Profiling")
		
class KeyframePanel(bpy.types.Panel):
	bl_idname = "mn.keyframes"
	bl_label = "Keyframes"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Settings"
	
	@classmethod
	def poll(self, context):
		return context.space_data.tree_type == "AnimationNodeTreeType"
		
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		objects = getSelectedObjects()
		
		layout.label("Selected Objects: " + str(len(objects)))
		
		layout.prop(scene.mn_settings.keyframes, "selectedName", text = "Keyframe")
		
		name = scene.mn_settings.keyframes.selectedName
		type = getKeyframeType(name)
		
		row = layout.row()
		row.label("Type: " + str(type))
		
		if type == "Float":
			layout.prop(context.scene.mn_settings.keyframes, "selectedPath", text = "Path")
			setTransformsKeyframe = layout.operator("mn.set_float_keyframe", text = "Set Value From Path")
			setTransformsKeyframe.keyframeName = name
			setTransformsKeyframe.dataPath = context.scene.mn_settings.keyframes.selectedPath
			
		elif type == "Transforms":
			setTransformsKeyframe = layout.operator("mn.set_transforms_keyframe", text = "Set Current Transforms As Keyframe")
			setTransformsKeyframe.keyframeName = name
		
		for object in objects:
			box = layout.box()
			row = box.row()
			row.prop(object, "name", text = "")
			
			remove = row.operator("mn.remove_keyframe_from_object", text = "Remove Keyframe")
			remove.objectName = object.name
			remove.keyframeName = name
			
			drawKeyframeInput(box, object, name)
		
		
class ForceNodeTreeUpdate(bpy.types.Operator):
	bl_idname = "mn.force_full_update"
	bl_label = "Force Node Tree Update"

	def execute(self, context):
		resetCompileBlocker()
		updateAnimationTrees(treeChanged = True)
		return {'FINISHED'}
		
class PrintNodeTreeExecutionStrings(bpy.types.Operator):
	bl_idname = "mn.print_node_tree_execution_string"
	bl_label = "Print Node Tree Code"

	def execute(self, context):
		print()
		for codeString in getCodeStrings():
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
		text = getNormalNodeTemplate() + getAutoRegisterCode()
		textBlock.from_string(text)
		textBlock.use_tabs_as_spaces = True
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
						space.text.clear()
						space.text.write(textString)
		return {'FINISHED'}
	

# custom nodes
##############################
	

def getAllAnimationNodeClasses():
	from mn_node_base import AnimationNode
	return AnimationNode.__subclasses__()
def getCustomNodeClasses():
	from mn_node_register import getAllNodeIdNames
	officialNodeNames = getAllNodeIdNames()
	nodeClasses = []
	foundNames = []
	for nodeClass in getAllAnimationNodeClasses():
		if nodeClass.bl_idname not in officialNodeNames and nodeClass.bl_idname not in foundNames:
			nodeClasses.append(nodeClass)
			foundNames.append(nodeClass.bl_idname)
	return nodeClasses
def getCustomCategories():
	nodeClasses = getCustomNodeClasses()
	categories = set()
	for nodeClass in nodeClasses:
		category = getattr(nodeClass, "node_category", "None")
		categories.update([category])
	if len(categories) == 0: categories.update(["None"])
	return categories
def getCustomNodeCategoryItems(self, context):
	categories = getCustomCategories()
	items = []
	for category in categories:
		items.append((category, category, ""))
	return items
	
def getCustomNodesInCategory(category):
	nodeClasses = getCustomNodeClasses()
	nodeClassesInCategory = []
	for nodeClass in nodeClasses:
		if getattr(nodeClass, "node_category", "None") == category:
			nodeClassesInCategory.append(nodeClass)
	return nodeClassesInCategory

def getCustomNodes(self, context):
	return [("mn_TimeInfoNode", "Time Info", "")]
	
bpy.types.Scene.customNodeCategory = bpy.props.EnumProperty(items = getCustomNodeCategoryItems, name = "Custom Categories")