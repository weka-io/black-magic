import sys
import os.path
__termenu_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'termenu'))
if __termenu_path not in sys.path:
    sys.path.insert(0, __termenu_path)


import inspect
import gc

from termenu.app import AppMenu


class Action:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


class PickIt(Action):
    pass


class ExploreIt(Action):
    pass


class ReferrerExplorer(AppMenu):
    def title(self):
        return 'Pick referrer to explore %r' % (self.obj)

    def __init__(self, obj, *, ignore):
        self.obj = obj
        self.ignore = ignore
        super().__init__()

    @property
    def items(self):
        referrers = gc.get_referrers(self.obj)
        yield 'BOLD<<PICK THIS ONE>>', PickIt(self.obj)
        currentframe = inspect.currentframe()
        for referrer in referrers:
            if referrer in (currentframe, self, self.__dict__):
                continue
            yield referrer, ExploreIt(referrer)

    def action(self, value):
        self.result(value)


def explore_gc_graph(obj):
    currentframe = inspect.currentframe()
    while True:
        explorer = ReferrerExplorer(obj, ignore=(currentframe,))
        if isinstance(explorer.return_value, PickIt):
            return explorer.return_value.value
        elif isinstance(explorer.return_value, ExploreIt):
            obj = explorer.return_value.value
            del explorer
            gc.collect()

if __name__ == "__main__":
    foo = object()
    ref1 = [1, 2, foo]
    ref2 = {'a': 1, 'b': 2, 'foo': foo}
    ref3 = {1, 2, foo}
    def ref4():
        return foo

    obj = explore_gc_graph(foo)

    print('chosen object is', obj)
