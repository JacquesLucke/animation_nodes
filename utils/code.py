import ast

def isCodeValid(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
