import bpy

from . import utils
from . import keymap
from . import id_keys
from . import draw_handler
from . ui import node_panel
from . ui import node_colors
from . import extend_bpy_types
from . operators import dynamic_operators
from . base_types import node as node_base
from . nodes.sound import bake as sound_bake
from . base_types import socket as socket_base
from . ui.node_menu import registerMenu, unregisterMenu

def registerFiles():
    node_base.register()
    node_panel.register()
    sound_bake.register()
    socket_base.register()
    node_colors.register()
    utils.operators.register()
    extend_bpy_types.register()
    dynamic_operators.register()
    utils.handlers.registerHandlers()
    id_keys.object_extension.register()

    registerMenu()
    keymap.register()

def unregisterFiles():
    node_base.unregister()
    node_panel.unregister()
    sound_bake.unregister()
    socket_base.unregister()
    node_colors.unregister()
    draw_handler.unregister()
    utils.operators.unregister()
    extend_bpy_types.unregister()
    dynamic_operators.unregister()
    utils.handlers.unregisterHandlers()
    id_keys.object_extension.unregister()

    unregisterMenu()
    keymap.unregister()
