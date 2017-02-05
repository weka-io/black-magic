#!/usr/bin/python
import dis
import itertools
from inspect import currentframe


def named_unpack(source):
    frame = currentframe().f_back

    iterator = dis.get_instructions(frame.f_code)
    for instruction in iterator:
        if instruction.offset == frame.f_lasti:
            break

    if instruction.opname == 'UNPACK_SEQUENCE':
        for instruction in itertools.islice(iterator, instruction.argval):
            yield getattr(source, instruction.argval)
    elif instruction.opname == 'FOR_ITER':
        instruction = next(iterator)
        assert instruction.opname == 'UNPACK_SEQUENCE'
        unpack_instructions = list(itertools.islice(iterator, instruction.argval))
        assert all(instruction.opname in {'STORE_NAME', 'STORE_FAST'} for instruction in unpack_instructions)
        for entry in source:
            yield (getattr(entry, instruction.argval) for instruction in unpack_instructions)
    else:
        raise Exception("Can't handle op %s" % instruction.opname)


if __name__ == '__main__':
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
