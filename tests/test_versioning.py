import pytest

from black_python_magic.versioning import versioned, VersionError


def test_versioning():
    class Foo:
        def __init__(self, version):
            self._version = version

        @versioned(min=1, max=1)
        def foo(self, a):
            return 'version 1: (%s)' % (a,)

        @versioned(max=2)
        def foo(self, a, b):
            return 'version 2: (%s, %s)' % (a, b)

    foo0 = Foo(0)
    foo1 = Foo(1)
    foo2 = Foo(2)
    foo3 = Foo(3)

    with pytest.raises(VersionError):
        foo0.foo
    assert foo1.foo(a=1) == 'version 1: (1)'
    assert foo2.foo(a=2, b=3) == 'version 2: (2, 3)'
    with pytest.raises(VersionError):
        foo3.foo
