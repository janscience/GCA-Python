import re


def getattr_maybelist(obj, name):
    if obj is None:
        return []
    if type(obj) == list:

        if name.startswith('[') and name.endswith(']'):
            idx = int(name[1:-1])
            return [obj[idx]] if idx < len(obj) else []

        return [x for o in obj for x in getattr_maybelist(o, name)]
    else:
        x = getattr(obj, name)
        return x if type(x) == list else [x]


def make_fields(field_str):
    return filter(lambda x: x is not None, re.split(ur'(?:\.|(?:(\[[0-9]+\])\.))', field_str))