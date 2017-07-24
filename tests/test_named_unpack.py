from python.named_unpack import named_unpack


def test_named_unpack():
    class Foo:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    c, a = named_unpack(Foo(a=1, b=2, c=3))
    assert a == 1
    assert c == 3

    def generator():
        for b, c in named_unpack([Foo(a=1, b=2, c=3),
                                  Foo(a=4, b=5, c=6),
                                  Foo(a=7, b=8, c=9)]):
            yield b, c
    assert list(generator()) == [(2, 3),
                                 (5, 6),
                                 (8, 9)]
