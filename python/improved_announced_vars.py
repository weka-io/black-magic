#!/usr/bin/python3
from contextlib import contextmanager

import logging


class MonkeyPatchLogger(object):
    @contextmanager
    def indented(self, *args, **kwargs):
        yield

    def announced_vars(self, header='With locals:', *args, **kwargs):
        "Announces the variables declared in the context"
        import inspect
        import dis
        frame = inspect.currentframe().f_back

        # `@contextmanager` annotates an internal `cm` function instead of the
        # `announced_vars` method so that `inspect.currentframe().f_back` will
        # point to the frame that uses `announced_vars`. If we decoraed
        # `announced_vars` with `@contextmanager`, we'd have to depend on
        # implementation details of `@contextmanager` - currently
        # `inspect.currentframe().f_back.f_back` would have worked, but we have
        # no guarantee that it'll remain like this forever.
        @contextmanager
        def cm():
            lasti_before = frame.f_lasti
            yield
            lasti_after = frame.f_lasti
            frame_locals = dict(frame.f_locals)
            prev_instruction = None

            def log_single_variable(name):
                try:
                    value = frame_locals[name]
                except KeyError:
                    pass
                else:
                    self.info('%s = %s', name, value)

            with self.indented(header, *args, footer=False, **kwargs):
                for instruction in dis.get_instructions(frame.f_code):
                    if instruction.offset <= lasti_before:
                        continue
                    if lasti_after <= instruction.offset:
                        break
                    if instruction.opname in {'STORE_NAME', 'STORE_FAST', 'STORE_GLOBAL'}:
                        log_single_variable(instruction.argval)
                    elif instruction.opname == 'POP_TOP' and prev_instruction and \
                            prev_instruction.opname in {'LOAD_NAME', 'LOAD_FAST', 'LOAD_GLOBAL'}:
                        log_single_variable(prev_instruction.argval)
                    prev_instruction = instruction

        return cm()


logging.Logger.__bases__ += (MonkeyPatchLogger,)


logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
if __name__ == '__main__':

    # Check outside function
    for _ in range(2):
        with _logger.announced_vars():
            a = 1
            b = 2

    c = 3
    with _logger.announced_vars():
        c

    # Check inside function
    def foo():
        for _ in range(2):
            with _logger.announced_vars():
                d = 4
                e = 5

        f = 6
        with _logger.announced_vars():
            f

    foo()
