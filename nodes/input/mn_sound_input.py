import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *
from mn_object_utils import *

class BakedSoundPropertyGroup(bpy.types.PropertyGroup):
	low = bpy.props.FloatProperty(name = "Lowest Frequency", default = 10.0)
	high = bpy.props.FloatProperty(name = "Highest Frequency", default = 5000.0)
	path = bpy.props.StringProperty(name = "Path", default = "")
	propertyName = bpy.props.StringProperty(name = "Property Path", default = "")

class SoundInputNode(Node, AnimationNode):
	bl_idname = "SoundInputNode"
	bl_label = "Sound Input"
	
	bakedSound = bpy.props.CollectionProperty(type = BakedSoundPropertyGroup)
	soundObjectName = bpy.props.StringProperty()
	
	def init(self, context):
		self.inputs.new("IntegerSocket", "Index")
		self.outputs.new("FloatSocket", "Strength")
		
	def draw_buttons(self, context, layout):
		bake = layout.operator("mn.bake_sound_to_node", "Bake")
		bake.nodeTreeName = self.id_data.name
		bake.nodeName = self.name
		loadSound = layout.operator("mn.set_sound_in_sequence_editor", "Load Sound")
		loadSound.filePath = self.bakedSound[0].path
		
	def execute(self, input):
		output = {}
		index = max(min(input["Index"], len(self.bakedSound)-1), 0)
		soundObject = self.getSoundObject()
		output["Strength"] = soundObject[self.bakedSound[index].propertyName]
		return output
		
	def bakeSound(self, filePath):
		bpy.context.scene.frame_current = 1
		soundObject = self.getSoundObject()
		self.removeSoundCurves(soundObject)
		self.bakeIndividualSound(soundObject, filePath, 10, 200)
		self.bakeIndividualSound(soundObject, filePath, 200, 500)
		self.bakeIndividualSound(soundObject, filePath, 500, 1000)
		soundObject.hide = True
		
	def getSoundObject(self):
		soundObject = bpy.data.objects.get(self.soundObjectName)
		if soundObject is None:
			soundObject = bpy.data.objects.new(getPossibleObjectName("sound object"), None)
			self.soundObjectName = soundObject.name
			bpy.context.scene.objects.link(soundObject)
		return soundObject
		
	def removeSoundCurves(self, soundObject):
		for item in self.bakedSound:
			fCurve = getFCurveWithDataPath(soundObject, '["' + item.propertyName + '"]')
			if fCurve is not None:
				soundObject.animation_data.action.fcurves.remove(fCurve)
		self.bakedSound.clear()
		
	def bakeIndividualSound(self, soundObject, filePath, low, high):
		propertyName = "sound " + str(low) + " - " + str(high)
		propertyPath = '["' + propertyName + '"]'
		deselectAllFCurves(soundObject)
		soundObject[propertyName] = 0.0
		soundObject.keyframe_insert(frame = 1, data_path = propertyPath)
		bpy.context.area.type = "GRAPH_EDITOR"
		soundObject.hide = False
		deselectAll()
		setActive(soundObject)
		bpy.ops.graph.sound_bake(
			filepath = filePath,
			low = low,
			high = high)
		bpy.context.area.type = "NODE_EDITOR"
		
		item = self.bakedSound.add()
		item.low = low
		item.high = high
		item.path = filePath
		item.propertyName = propertyName
		
	def copy(self, node):
		self.soundObjectName = ""
		self.bakedSound.clear()
		
class BakeSoundToNode(bpy.types.Operator):
	bl_idname = "mn.bake_sound_to_node"
	bl_label = "Bake Sound to Node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype = "FILE_PATH")
	
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return { 'RUNNING_MODAL' }
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.bakeSound(self.filepath)
		return {'FINISHED'}	
		
class SetSoundInSequenceEditor(bpy.types.Operator):
	bl_idname = "mn.set_sound_in_sequence_editor"
	bl_label = "Load Sound in Blender"
	
	filePath = bpy.props.StringProperty()
		
	def execute(self, context):
		scene = bpy.context.scene
		scene.sequence_editor_clear()
		scene.sequence_editor_create()
		scene.sequence_editor.sequences.new_sound("Sound", self.filePath, channel = 0, frame_start = 1)
		return {'FINISHED'}	
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)