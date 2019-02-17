from black_python_magic.generics import Generic, genericmethod


def test_generic_list():
    class GenericList(list, Generic):
        pass

    class Foo:
        def __init__(self, num):
            self.num = num

        def __repr__(self):
            return '%s(%s)' % (type(self).__name__, self.num)

        @genericmethod(list)
        @property
        def sum_squares(lst):
            return sum(foo.num ** 2 for foo in lst)

    foos = GenericList[Foo]([Foo(1), Foo(2)])

    assert foos.sum_squares == 5
