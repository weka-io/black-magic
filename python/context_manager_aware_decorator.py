#!/usr/bin/python
from contextlib import contextmanager
from functools import wraps


_contextmanager_code_object = contextmanager(lambda: None).__code__


def context_manager_aware_decorator(deco):
    @wraps(deco)
    def wrapper(func, *args, **kwargs):
        if func.__code__ == _contextmanager_code_object:  # Context manager - wrap normally
            return deco(func, *args, **kwargs)
        else:
            @wraps(func)
            @contextmanager
            def func_as_cm(*args, **kwargs):
                yield func(*args, **kwargs)

            decorated = deco(func_as_cm, *args, **kwargs)

            @wraps(decorated)
            def uncm_decorated(*args, **kwargs):
                with decorated(*args, **kwargs) as result:
                    return result

            return uncm_decorated

    return wrapper
