from operator import attrgetter


class LateDecoratorDescriptor:
    def __init__(self, decorator_factory, func):
        self.decorator_factory = decorator_factory
        self.func = func

    def __get__(self, instance, owner):
        method = self.func.__get__(instance, owner)
        if instance is None:
            return method
        else:
            decorator = self.decorator_factory(instance)
            return decorator(method)


def late_decorator(decorator_factory):
    """
    Create and apply a decorator only after the method is instantiated.

    code-block::

        class UsageWithLambda:
            @late_decorator(lambda self: some_decorator_that_needs_the_object(self))
            def foo(self):
                # ...
        class UsageWithAttribute:
            def decorator_method(self, func):
                # ...
            @late_decorator('decorator_method')
            def foo(self):
                # ...
    """

    if callable(decorator_factory):
        pass
    elif isinstance(decorator_factory, str):
        decorator_factory = attrgetter(decorator_factory)
    else:
        raise TypeError('decorator_factory must be callable or string, not %s' % type(decorator_factory))

    def wrapper(func):
        return LateDecoratorDescriptor(decorator_factory, func)
    return wrapper
