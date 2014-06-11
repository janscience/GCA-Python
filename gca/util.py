

class Selector(object):
    def __init__(self, name):
        self.name = name

    def __getitem__(self, item):
        return item

    def __call__(self, name, idx):
        return True


class ArraySelector(Selector):
    def __init__(self, name, index):
        super(ArraySelector, self).__init__(name)
        self.index = index

    def __call__(self, name, idx):
        return idx == self.index


class ListSelector(Selector):
    def __init__(self, name, inner):
        super(ListSelector, self).__init__(name)
        self.lst = [x.strip() for x in reversed(inner.split(';'))]

    def __getitem__(self, item):
        if not item:
            return item
        idx = [i for i, n in enumerate(self.lst) if item.startswith(n)]
        return str(idx[0]) if len(idx) else ""


def getattr_maybelist(obj, sel):
    if obj is None:
        return []
    if type(obj) == list:
        return [x for o in obj for x in getattr_maybelist(o, sel)]
    else:
        x = getattr(obj, sel.name)
        val = x if type(x) == list else [x]
        return [sel[v] for iv, v in enumerate(val) if sel(v, iv)]


def make_selector(string):
    x = string.rfind('[')
    y = string.rfind(']')
    if x != -1 and y != -1:
        idx = int(string[x+1:y])
        return ArraySelector(string[:x], idx)
    x = string.rfind('{')
    y = string.rfind('}')
    if x != -1 and y != -1:
        inner = string[x+1:y]
        name = string[:x]
        return ListSelector(name, inner)
    return Selector(string)


def make_fields(field_str):
    fields = field_str.split('.')
    return map(make_selector, fields)