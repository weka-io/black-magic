from collections import OrderedDict


class ConstructMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        base, = bases
        return base.__dict__['custom_dsl']()

    def __new__(cls, name, bases, dct):
        if name is None:
            return super(ConstructMeta, cls).__new__(cls, '__CONSTRUCT_HELPER__', bases, dct)
        else:
            dct.pop('__module__')
            dct.pop('__qualname__', None)
            base, = bases
            params = base.__dict__
            return params['build_dlg'](dct)


def construct(build_dlg, custom_dsl=None):
    if custom_dsl is None:
        custom_dsl = OrderedDict
    else:
        assert hasattr(type, '__prepare__'), 'Cannot use DSL - this version of python does not support __prepare__'

    return ConstructMeta(None, (), dict(
        custom_dsl=custom_dsl,
        build_dlg=build_dlg,
    ))


def construct_kwargs(cls, custom_dsl=None):
    def build_dlg(dct):
        return cls(**dct)

    return construct(build_dlg, custom_dsl=custom_dsl)
