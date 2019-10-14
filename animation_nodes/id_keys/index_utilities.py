import bpy
import random
from bpy.props import *
from .. utils.blender_ui import getDpiFactor, redrawAll

def getObjectsIDKeys():
    object_list=[]
    for obj in bpy.context.selected_objects:
        try:
            obj["AN*Integer*Index"]
            object_list.append(obj)
        except KeyError: pass
    sorted_list = sorted(object_list, key=lambda obj: obj["AN*Integer*Index"])
    return sorted_list

def sortListByIDKey(list):
    sorted_list = sorted(list, key=lambda obj: obj["AN*Integer*Index"])
    return sorted_list

class IndexOffset(bpy.types.Operator):
    bl_idname = "an.index_offset"
    bl_label = "Index Offset"
    bl_description = "Offset Index of selected Objects"

    offset_type: EnumProperty(
        name="Type",
        default='ADD',
        items=(
            ('ADD', "Add",
             "Add number to every selected object which have Index key.\n"
             "Before :\n"
             "0, 1, 2, 3\n"
             "After Offset 1 :\n"
             "1, 2, 3, 4"),
            ('RANDOMIZE', "Randomize",
             "Randomize Index key for all selected objects which have Index Key.\n"
             "Before :\n"
             "0, 1, 2, 3\n"
             "After :\n"
             "1, 3, 0, 2"),
            ('REVERT', "Revert",
             "Revert Index for every selected object which have Index Key.\n"
             "Before :\n"
             "0, 1, 2, 3\n"
             "After :\n"
             "3, 2, 1, 0"),
            ('FILL', "Fill Gaps",
             "Fill Gaps in a serie of Index.\n"
             "Before :\n"
             "0, 1, 3, 4\n"
             "After :\n"
             "0, 1, 2, 3"),
        ))
    offset_value: IntProperty(name="Offset value", default=0)
    random_method: EnumProperty(
        name="Method",
        default='EXISTING',
        items=(
            ('EXISTING', "Existing",
             "Randomize existing indexes through selected objects."),
            ('CREATE', "Create",
             "Create random index for each selected object."),
        ))
    random_seed: IntProperty(name="Seed", default=0)
    random_min: IntProperty(name="Min", default=0)
    random_max: IntProperty(name="Max", default=10)
    start_at: BoolProperty(name="Start at", default=False)
    remove_gaps: BoolProperty(name="Remove gaps", default=False)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250 * getDpiFactor())

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "offset_type", expand = True)
        if self.offset_type=="ADD":
            layout.prop(self, "offset_value")
        elif self.offset_type=="RANDOMIZE":
            layout.prop(self, "random_method", text="")
            if self.random_method=="CREATE":
                row=layout.row(align=True)
                row.prop(self, "random_min")
                row.prop(self, "random_max")
            else: layout.prop(self, "random_seed")
        elif self.offset_type=="REVERT":
            layout.prop(self, "remove_gaps")
            if self.remove_gaps:
                row = layout.row()
                row.prop(self, "start_at")
                if self.start_at: row.prop(self, "offset_value", text="")
        elif self.offset_type=="FILL":
            row=layout.row()
            row.prop(self, "start_at")
            if self.start_at: row.prop(self, "offset_value", text="")

    def check(self, context):
        return True

    def execute(self, context):
        object_list=getObjectsIDKeys()
        if self.offset_type=="ADD":
            for obj in object_list: obj["AN*Integer*Index"]=obj["AN*Integer*Index"]+self.offset_value
        elif self.offset_type=="RANDOMIZE":
            if self.random_method=="EXISTING":
                random_numbers=[i for i in range(len(object_list))]
                random.seed(self.random_seed)
                random.shuffle(random_numbers)
            else:
                try: random_numbers=random.sample(range(self.random_min, self.random_max), len(object_list))
                except ValueError: random_numbers = random.sample(range(self.random_min, len(object_list)), len(object_list))
            for obj in object_list: obj["AN*Integer*Index"] = random_numbers[object_list.index(obj)]
        elif self.offset_type == "REVERT":
            if self.remove_gaps:
                if self.start_at: offset = self.offset_value
                else: offset = object_list[0]["AN*Integer*Index"]
                object_list.reverse()
                for obj in object_list: obj["AN*Integer*Index"] = object_list.index(obj)+offset
            else:
                index_list = []
                for obj in object_list: index_list.append(obj["AN*Integer*Index"])
                index_list.reverse()
                for obj in object_list: obj["AN*Integer*Index"]=index_list[object_list.index(obj)]
        elif self.offset_type == "FILL":
            if self.start_at: offset=self.offset_value
            else: offset=object_list[0]["AN*Integer*Index"]
            for obj in object_list: obj["AN*Integer*Index"] = object_list.index(obj)+offset
        redrawAll()
        self.offset_value=0
        return {'FINISHED'}
