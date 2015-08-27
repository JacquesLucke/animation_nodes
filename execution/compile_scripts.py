import sys
from .. problems import InvalidSyntax

def compileScript(script, name = "<string>"):
    try:
        return compile(script, name, "exec")
    except SyntaxError:
        lines = []
        lineNumber = sys.exc_info()[1].lineno
        for i, line in enumerate(script.split("\n")):
            if i + 1 == lineNumber: lines.append(str(i+1) + ".  " + line + "        <-------------- Error happens here")
            else: lines.append(str(i+1) + ".  " + line)
        InvalidSyntax(code = "\n".join(lines)).report()
