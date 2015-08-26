def splitAlignment(layout):
    row = layout.row()
    left = row.row()
    left.alignment = "LEFT"
    right = row.row()
    right.alignment = "RIGHT"
    return left, right
