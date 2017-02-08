#!/usr/bin/python3
from contextlib import contextmanager

import logging
logging.basicConfig()

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
            with self.indented(header, *args, footer=False, **kwargs):
                for instruction in dis.get_instructions(frame.f_code):
                    if instruction.offset <= lasti_before:
                        continue
                    if lasti_after <= instruction.offset:
                        break
                    if instruction.opname in {'STORE_NAME', 'STORE_FAST'}:
                        name = instruction.argval
                        try:
                            value = frame_locals[name]
                        except KeyError:
                            pass
                        else:
                            self.info('%s = %s', name, value)

        return cm()


logging.Logger.__bases__ += (MonkeyPatchLogger,)


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


for _ in range(2):
    with _logger.announced_vars():
        a = 1
        b = 2


def foo():
    for _ in range(2):
        with _logger.announced_vars():
            c = 3
            d = 4


foo()
