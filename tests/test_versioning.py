import pytest

from black_python_magic.versioning import versioned, VersionError


def test_versioning_basic():
    class Foo:
        def __init__(self, version):
            self._version = version

        @versioned(max=4)
        def foo(self, a):
            return 'old: (%s)' % (a,)

        @versioned()
        def foo(self, a, b):
            return 'new: (%s, %s)' % (a, b)

    # Foos with version up to 4 use the old foo()
    assert Foo(1).foo(a=2) == 'old: (2)'
    assert Foo(3).foo(a=4) == 'old: (4)'

    # Foos with version above 4 use the new foo()
    assert Foo(5).foo(a=6, b=7) == 'new: (6, 7)'
    assert Foo(8).foo(a=9, b=10) == 'new: (9, 10)'


def test_versioning_lower_and_upper_bounds():
    class Foo:
        def __init__(self, version):
            self._version = version

        @versioned(min=1, max=1)
        def foo(self, a):
            return 'version 1: (%s)' % (a,)

        @versioned(max=2)
        def foo(self, a, b):
            return 'version 2: (%s, %s)' % (a, b)

    # Foos with version below 1 do not have foo()
    with pytest.raises(VersionError):
        Foo(0).foo

    assert Foo(1).foo(a=1) == 'version 1: (1)'
    assert Foo(2).foo(a=2, b=3) == 'version 2: (2, 3)'

    # Foos with version above 2 do not have foo()
    with pytest.raises(VersionError):
        Foo(3).foo
