import hashlib

# Changing this function can result in broken files
def hashStringToNumber(text):
    md5 = hashlib.md5()
    md5.update(text.encode("utf-8"))
    number = int(int(md5.hexdigest(), 16) % 1e8)
    return number
