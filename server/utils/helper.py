import uuid

def str_to_utf8(value):
    return bytes(value,'utf-8')

def get_uuid():
    return str(uuid.uuid4())