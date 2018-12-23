import pytest

from black_python_magic.strict_api import StrictApi


def test_strict_api():
    class Api:
        def foo(self): ...

        def bar(self): ...

    class Concrete():
        def foo(self):
            return 1

        def bar(self):
            return 2

        def baz(self):
            return 3

    concrete = Concrete()
    api = StrictApi[Api](concrete)

    assert concrete.foo() == api.foo() == 1

    assert concrete.bar() == api.bar() == 2

    assert concrete.baz() == 3
    with pytest.raises(AttributeError):
        api.baz()


def test_strict_api_annotatated_result():
    class Api1:
        def foo(self): ...

    class Api2:
        def bar(self) -> Api1: ...

    class Concrete1:
        def foo(self):
            return 1

        def baz(self):
            return 2

    class Concrete2:
        def bar(self):
            return Concrete1()

    concrete2 = Concrete2()
    concrete1 = concrete2.bar()

    api2 = StrictApi[Api2](concrete2)
    api1 = api2.bar()

    assert concrete1.foo() == api1.foo() == 1

    assert concrete1.baz() == 2
    with pytest.raises(AttributeError):
        api1.baz()
