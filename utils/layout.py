import textwrap

def splitAlignment(layout):
    row = layout.row()
    left = row.row()
    left.alignment = "LEFT"
    right = row.row()
    right.alignment = "RIGHT"
    return left, right

def writeText(layout, text, width = 30, icon = "NONE"):
    col = layout.column(align = True)
    col.scale_y = 0.85
    prefix = " "
    for line in textwrap.wrap(text, width):
        col.label(prefix + line, icon = icon)
        if icon != "NONE": prefix = "     "
        icon = "NONE"
