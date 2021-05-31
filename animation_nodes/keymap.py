import bpy

addon_keymaps = []

def register():
    if not canRegisterKeymaps(): return
    
    addon_keymaps.clear()
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")

    # Open the ctrl-A search menu
    kmi = km.keymap_items.new("an.node_search", type = "A", value = "PRESS", ctrl = True)
    addon_keymaps.append((km, kmi))

    # Open the context sensitive pie menu
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "W", value = "PRESS")
    kmi.properties.name = "AN_MT_context_pie"
    addon_keymaps.append((km, kmi))

    # Move view to subprogram nodes
    kmi = km.keymap_items.new("an.network_navigation", type = "TAB", value = "PRESS")
    addon_keymaps.append((km, kmi))

    # Selection Pie Menu
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "E", value = "PRESS")
    kmi.properties.name = "AN_MT_selection_pie"
    addon_keymaps.append((km, kmi))

    # Floating Node Settings
    kmi = km.keymap_items.new("an.floating_node_settings_panel", type = "U", value = "PRESS")
    addon_keymaps.append((km, kmi))

    # Deactivate Auto Execution
    kmi = km.keymap_items.new("an.deactivate_auto_execution", type = "Q", value = "PRESS", ctrl = True, shift = True)
    addon_keymaps.append((km, kmi))

def unregister():
    if not canRegisterKeymaps(): return

    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def canRegisterKeymaps():
    return not bpy.app.background
