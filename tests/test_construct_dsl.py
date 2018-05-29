import pytest
import inspect

from black_python_magic.construct_dsl import construct, construct_kwargs

from collections import OrderedDict
from weakref import WeakValueDictionary


def test_construct_dsl():
    class foo(construct(dict)):
        a = 1
        b = 2

    assert type(foo) is dict
    assert foo == dict(a=1, b=2)

    class bar(construct(OrderedDict)):
        a = 1
        b = 2

    class baz(construct(OrderedDict)):
        b = 2
        a = 1

    assert type(bar) == type(baz) == OrderedDict

    assert bar != baz
    assert bar == dict(a=1, b=2) == baz

    class X:
        pass

    x1 = X()
    x2 = X()

    class qux(construct(WeakValueDictionary)):
        a = x1
        b = x2

    assert type(qux) is WeakValueDictionary
    assert qux == dict(a=x1, b=x2)
    del x1
    assert qux == dict(b=x2)


def test_construct_dsl_kwargs():
    class Foo:
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def __eq__(self, other):
            return self.a == other.a and self.b == other.b

    with pytest.raises(TypeError):
        class foo1(construct(Foo)):
            a = 1
            b = 2


    class foo2(construct_kwargs(Foo)):
        a = 1
        b = 2

    assert type(foo2) is Foo
    assert foo2 == Foo(a=1, b=2)

    with pytest.raises(TypeError):
        class foo3(construct_kwargs(Foo)):
            a = 1


def test_construct_dsl_custom_dsl():
    class Dsl(OrderedDict):
        def __getitem__(self, name):
            try:
                return getattr(self, name)
            except AttributeError:
                return super().__getitem__(name)

        def stringify(self, name):
            self[name] = str(self[name])

        def double(self, name):
            self[name] *= 2

    class foo(construct(dict, Dsl)):
        a = 1
        b = 2
        stringify('a')
        double('b')

    assert foo == dict(a='1', b=4)


def test_construct_dsl_accurate_line_error():
    class NegativeNumberException(Exception):
        pass

    class Dsl(OrderedDict):
        def __setitem__(self, name, value):
            if isinstance(value, int) and value < 0:
                raise NegativeNumberException
            return super().__setitem__(name, value)

    frame_data = {}

    with pytest.raises(NegativeNumberException) as excinfo:
        class foo(construct(dict, Dsl)):
            a = 1
            frame = inspect.currentframe()
            frame_data['code'] = frame.f_code
            frame_data['line'] = frame.f_lineno
            b = -2
            c = 3

    tb = excinfo.value.__traceback__
    while tb.tb_frame.f_code is not frame_data['code']:
        tb = tb.tb_next

    assert tb.tb_lineno == frame_data['line'] + 1
