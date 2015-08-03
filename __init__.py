'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name":        "Animation Nodes",
    "description": "Node system for more flexible animations.",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 7),
    "blender":     (2, 7, 4),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     "Stable, but some things may change in the future."
    }



# load and reload submodules
##################################

from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# properties
##################################

import bpy
from bpy.props import *
from . mn_execution import nodeTreeChanged
from . id_keys import idTypeItems

class GlobalUpdateSettings(bpy.types.PropertyGroup):
    frameChange = BoolProperty(default = True, name = "Frame Change", description = "Recalculate the nodes when the frame has been changed")
    sceneUpdate = BoolProperty(default = True, name = "Scene Update", description = "Recalculate the nodes continuously")
    propertyChange = BoolProperty(default = True, name = "Property Change", description = "Recalculate the nodes when a property of a node changed")
    treeChange = BoolProperty(default = True, name = "Tree Change")
    skipFramesAmount = IntProperty(default = 0, name = "Skip Frames", min = 0, soft_max = 10, description = "Only recalculate the nodes every nth frame")
    redrawViewport = BoolProperty(default = True, name = "Redraw Viewport", description = "Redraw the UI after each execution. Turning it off gives a better performance but worse realtime feedback.")
    resetCompileBlockerWhileRendering = BoolProperty(default = True, name = "Force Update While Rendering", description = "Force the node tree to execute if the frame changes and Blender is rendering currently (nodes which change the frame may lock the UI)")

class DeveloperSettings(bpy.types.PropertyGroup):
    printUpdateTime = BoolProperty(default = False, name = "Print Global Update Time")
    printGenerationTime = BoolProperty(default = False, name = "Print Script Generation Time")
    executionProfiling = BoolProperty(default = False, name = "Node Execution Profiling", update = nodeTreeChanged)

class IDKeyType(bpy.types.PropertyGroup):
    name = StringProperty()
    id = StringProperty()
    type = StringProperty()
    hide = BoolProperty(default = False)

class IDKeySettings(bpy.types.PropertyGroup):
    keys = CollectionProperty(type = IDKeyType)
    newKeyName = StringProperty(default = "Initial Transforms")
    newKeyType = EnumProperty(items = idTypeItems, name = "Type", default = "Transforms")
    showAdvanced = BoolProperty(name = "Show Advanced", default = True, description = "Show more options for each ID Key")

class AnimationNodesSettings(bpy.types.PropertyGroup):
    update = PointerProperty(type = GlobalUpdateSettings, name = "Update Settings")
    developer = PointerProperty(type = DeveloperSettings, name = "Developer Settings")
    idKeys = PointerProperty(type = IDKeySettings, name = "ID Keys")



# register
##################################

addon_keymaps = []
def register_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")
    kmi = km.keymap_items.new("mn.insert_node", type = "A", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "W", value = "PRESS")
    kmi.properties.name = "mn.context_pie"
    addon_keymaps.append(km)

def unregister_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

from . insert_nodes_menu import registerMenu, unregisterMenu
from . import manage_broken_files as manage_broken_files
from . import mn_execution as execution
from . base_types import node as node_base
from . base_types import node_function_call
from . nodes.sound import sequencer_sound_input as sequencer_sound

def register():
    bpy.utils.register_module(__name__)
    manage_broken_files.register_handlers()
    execution.register_handlers()
    node_base.register_handlers()
    node_function_call.register_handlers()
    sequencer_sound.register_handlers()
    registerMenu()
    register_keymaps()
    bpy.types.Scene.mn_settings = PointerProperty(type = AnimationNodesSettings, name = "Animation Node Settings")

    print("Registered Animation Nodes with {} modules.".format(len(modules)))

def unregister():
    unregister_keymaps()
    bpy.utils.unregister_module(__name__)
    manage_broken_files.unregister_handlers()
    execution.unregister_handlers()
    node_base.unregister_handlers()
    node_function_call.unregister_handlers()
    sequencer_sound.unregister_handlers()
    unregisterMenu()

    print("Unregistered Animation Nodes")
