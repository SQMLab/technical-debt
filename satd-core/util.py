import hashlib

def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()