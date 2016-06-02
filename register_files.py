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
    id_keys.register()
    node_base.register()
    sound_bake.register()
    socket_base.register()
    node_colors.register()
    draw_handler.register()
    utils.operators.register()
    extend_bpy_types.register()
    dynamic_operators.register()
    node_panel.register()
    utils.handlers.registerHandlers()

    registerMenu()
    keymap.register()

def unregisterFiles():
    id_keys.unregister()
    node_base.unregister()
    sound_bake.unregister()
    socket_base.unregister()
    node_colors.unregister()
    draw_handler.unregister()
    utils.operators.unregister()
    extend_bpy_types.unregister()
    dynamic_operators.unregister()
    node_panel.unregister()
    utils.handlers.unregisterHandlers()

    unregisterMenu()
    keymap.unregister()
