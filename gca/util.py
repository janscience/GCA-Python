import re


def make_fields(field_str):
    return filter(lambda x: x is not None, re.split(ur'(?:\.|(?:(\[[0-9]+\])\.))', field_str))