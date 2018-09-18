import sys
import os.path

for __dep in ('termenu', 'easypy'):
    __dep_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', __dep))
    if __dep_path not in sys.path:
        sys.path.insert(0, __dep_path)


import inspect
import gc
from collections import OrderedDict
import types
from itertools import chain

from termenu.app import AppMenu
from easypy.decorations import kwargs_resilient


class Action:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


class PickIt(Action):
    pass


class ExploreIt(Action):
    pass


class GoBack:
    pass


class ReferrerExplorer(AppMenu):
    def title(self):
        return 'Pick referrer to explore %s' % self.format_for_menu(self.obj)
        # return 'Pick referrer to explore %r' % (self.obj,)

    def __init__(self, obj, *, ignore, format_rules):
        self.obj = obj
        self.ignore = (self, self.__dict__) + ignore
        self.format_rules = format_rules
        super().__init__()

    @property
    def items(self):
        referrers = gc.get_referrers(self.obj)
        yield 'BOLD<<PICK THIS ONE>>', PickIt(self.obj)
        currentframe = inspect.currentframe()
        for referrer in referrers:
            if referrer is currentframe:
                continue
            if referrer in self.ignore:
                continue
            yield self.format_for_menu(referrer), ExploreIt(referrer)

    def action(self, value):
        self.result(value)

    def back(self):
        self.result(GoBack)

    def format_for_menu(self, obj):
        return apply_format_rules(
            obj, self.format_rules,
            orig_object=self.obj if self.obj is not obj else None)


def explore_gc_graph(obj):
    currentframe = inspect.currentframe()
    stack = []
    while True:
        explorer = ReferrerExplorer(obj, ignore=(currentframe, stack,), format_rules=FORMAT_RULES)
        if isinstance(explorer.return_value, PickIt):
            return explorer.return_value.value
        elif isinstance(explorer.return_value, ExploreIt):
            stack.append(obj)
            obj = explorer.return_value.value
            del explorer
            gc.collect()
        elif explorer.return_value is GoBack:
            if not stack:
                return
            obj = stack.pop()
            del explorer
            gc.collect()


def apply_format_rules(obj, format_rules, orig_object):
    fields = OrderedDict()

    target_object = [obj]
    while target_object:
        obj = target_object.pop()
        assert not target_object, 'multiple objects returned: %s' % target_object
        for rule in format_rules:
            try:
                typ = rule.__annotations__['obj']
            except KeyError:
                pass
            else:
                if not isinstance(obj, typ):
                    continue
            switch_with = rule(obj=obj, fields=fields, orig_object=orig_object)
            if switch_with is not None:
                target_object.append(switch_with)


    result = 'BOLD<<%s>> %s' % (type(obj).__name__, id(obj))

    if fields:
        result = '%s\t%s' % (
            result,
            '\t'.join('BOLD<<%s>>: %s' % (k, v) for k, v in fields.items()))
    return result


FORMAT_RULES = []


def format_rule(func):
    FORMAT_RULES.append(kwargs_resilient(func))
    return func


def CellType():
    x = 1
    def foo():
        return x
    return type(foo.__closure__[0])
CellType = CellType()


def scale_referrers(obj, *preds):
    try:
        pred, *next_preds = preds
    except ValueError:
        yield obj
        return
    if isinstance(pred, type):
        pred = pred.__instancecheck__
    for referrer in gc.get_referrers(obj):
        if pred(referrer):
            yield from scale_referrers(referrer, *next_preds)


@format_rule
def extract_name(obj, fields):
    for attr in ('name', '_name', '_qualname', '__name__'):
        name = getattr(obj, attr, None)
        if name:
            fields['name'] = name
            fields.move_to_end('name', last=False)
            return


@format_rule
def process_dict(obj: dict, fields, orig_object):
    if orig_object:
        fields['referent_key'] = [k for k, v in obj.items() if v is orig_object]

    for referrer in gc.get_referrers(obj):
        if getattr(referrer, '__dict__', None) is obj:
            return referrer

    fields['len'] = len(obj)


@format_rule
def process_cell(obj: CellType, fields):
    fn, = scale_referrers(obj, tuple, types.FunctionType)
    fields['varname'] = fn.__code__.co_freevars[fn.__closure__.index(obj)]
    return fn


if __name__ == "__main__":
    foo = object()
    ref1 = [1, 2, foo]
    ref2 = {'a': 1, 'b': 2, 'foo': foo}
    ref3 = {1, 2, foo}
    def ref4():
        return foo

    def ref5(x):
        def fn():
            return x
        return fn
    ref5 = ref5(foo)

    obj = explore_gc_graph(foo)

    print('chosen object is', obj)
