import bpy

def show_text(text, title = "", icon = "NONE"):
    bpy.context.window_manager.popup_menu(get_popup_drawer(text), title = title, icon = icon)

def get_popup_drawer(text):
    def draw_popup(menu, context):
        layout = menu.layout
        layout.label(text)
    return draw_popup
