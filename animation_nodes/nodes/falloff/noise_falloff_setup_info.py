def getExtensionArgs(utils):
    args = {}
    if utils.onLinux or utils.onMacOS:
        args["extra_compile_args"] = ["-std=c++11"]
    return args
