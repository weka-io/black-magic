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
