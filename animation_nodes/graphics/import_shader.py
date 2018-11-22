import gpu

def getShader(path):
    with open(path) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Fragment Shader" in line:
                index = i
                break
    return gpu.types.GPUShader("\n".join(lines[:i]), "\n".join(["\n"] * index + lines[i:]))
