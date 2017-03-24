import bpy

from . import utils
from . import keymap
from . import id_keys
from . import draw_handler
from . ui import node_panel
from . ui import node_colors
from . import extend_bpy_types
from . base_types.nodes import base_node
from . operators import dynamic_operators
from . nodes.sound import bake as sound_bake
from . base_types.sockets import base_socket
from . ui.node_menu import registerMenu, unregisterMenu

def registerFiles():
    base_node.register()
    node_panel.register()
    sound_bake.register()
    base_socket.register()
    node_colors.register()
    utils.operators.register()
    extend_bpy_types.register()
    dynamic_operators.register()
    utils.handlers.registerHandlers()
    id_keys.object_extension.register()

    registerMenu()
    keymap.register()

def unregisterFiles():
    base_node.unregister()
    node_panel.unregister()
    sound_bake.unregister()
    base_socket.unregister()
    node_colors.unregister()
    draw_handler.unregister()
    utils.operators.unregister()
    extend_bpy_types.unregister()
    dynamic_operators.unregister()
    utils.handlers.unregisterHandlers()
    id_keys.object_extension.unregister()

    unregisterMenu()
    keymap.unregister()
