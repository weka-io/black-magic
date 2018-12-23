import types
import threading
import functools


class StrictApiMeta(type):
    _SUBTYPES = {}
    _SUBTYPES_LOCK = threading.RLock()

    def __getitem__(cls, api):
        wrap_api = {}
        for k, v in api.__dict__.items():
            if isinstance(v, types.FunctionType):
                wrap_api[k] = StrictApiFunctionDescriptor(v)

        return type('%s[%s]' % (cls.__name__, api.__qualname__), (cls, api), wrap_api)


class StrictApi(metaclass=StrictApiMeta):
    def __init__(self, wrapped):
        self._wrapped = wrapped


class StrictApiFunctionDescriptor:
    def __init__(self, func):
        self.func = func
        self.return_api = func.__annotations__.get('return')

    def __get__(self, instance, owner):
        if instance is None:
            return self

        wrapped = instance._wrapped
        wrapped_func = getattr(wrapped, self.func.__name__)
        if self.return_api:
            @functools.wraps(wrapped_func)
            def wrapper(*args, **kwargs):
                result = wrapped_func(*args, **kwargs)
                result = StrictApi[self.return_api](result)
                return result
            return wrapper
        else:
            return wrapped_func
