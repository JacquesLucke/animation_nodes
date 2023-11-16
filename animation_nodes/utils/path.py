import os
import bpy
import ast
import functools

def getAbsolutePathOfSound(sound):
    return toAbsolutePath(sound.filepath, library = sound.library)

def toAbsolutePath(path, start = None, library = None):
    absPath = bpy.path.abspath(path, start, library)
    return os.path.normpath(absPath)

def toIDPropertyPath(name):
    return '["' + name + '"]'

def getResolvedNestedPath(id_block, path):
    blocks = parsePath(path)
    for i in reversed(range(len(blocks))):
        data = eval("id_block." + ".".join(blocks[:i + 1]))
        if isinstance(data, bpy.types.ID):
            return data, ".".join(blocks[i + 1:])
    return id_block, path

@functools.lru_cache()
def parsePath(expression):
    def split_internal(value):
        if isinstance(value, ast.Subscript):
            return split_internal(value.value) + [f'["{value.slice.value}"]']
        elif isinstance(value, ast.Attribute):
            return split_internal(value.value) + [value.attr]
        elif isinstance(value, ast.Name):
            return [value.id]
        else:
            raise NotImplementedError()

    tree = ast.parse(expression)
    tokens = split_internal(tree.body[0].value)

    blocks = tokens[:1]
    for t in tokens[1:]:
        if t.startswith("["):
            blocks[-1] += t
        else:
            blocks.append(t)
    return blocks
