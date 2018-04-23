import inspect
import functools


class VersionError(Exception):
    pass

class Versioned(object):
    def __init__(self, name):
        self._versions = []

    def _add_version(self, min_version, max_version, func):
        self._versions.append((min_version, max_version, func))
        functools.update_wrapper(self, func)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        try:
            version = instance._version
        except AttributeError:
            raise TypeError('%s does not have a `_version` - can not use versioned %s' % (instance, self.__name__))

        for min_version, max_version, func in self._versions:
            if min_version is not None and version < min_version:
                raise VersionError('Version is too low')
            if max_version is not None and max_version < version:
                continue
            return func.__get__(instance, owner)
        raise VersionError('Version is too high')


def versioned(min=None, max=None):
    """
    Create versioned functions
    """
    def wrapper(func):
        f_locals = inspect.currentframe().f_back.f_locals
        try:
            versioned = f_locals[func.__name__]
        except KeyError:
            versioned = Versioned(func.__name__)

        versioned._add_version(min, max, func)

        return versioned
    return wrapper
