from abc import ABCMeta


class GenericMeta(ABCMeta):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__instantiations = {}

    def __getitem__(cls, param):
        if hasattr(cls, '_generic_param_'):
            raise TypeError('%s is already instantiated' % cls)

        try:
            return cls.__instantiations[param]
        except KeyError:
            pass
        name = '%s[%s]' % (cls.__name__, param.__name__)
        new_type_dict = dict(
            __module__=cls.__module__,
            __qualname__=name,
            _generic_type_=cls,
            _generic_param_=param)

        for attr_name in dir(param):
            attr_value = getattr(param, attr_name)
            if isinstance(attr_value, GenericMethod) and issubclass(cls, attr_value.generic_type):
                new_type_dict[attr_name] = attr_value.func

        new_type = type(cls)(name, (cls,), new_type_dict)

        return new_type


class Generic(metaclass=GenericMeta):
    pass


class GenericMethod:
    def __init__(self, generic_type, func):
        self.generic_type = generic_type
        self.func = func


def genericmethod(generic_type):
    def wrapper(func):
        return GenericMethod(generic_type, func)

    return wrapper
