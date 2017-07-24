from contextlib import contextmanager

from python.context_manager_aware_decorator import context_manager_aware_decorator


def test_context_manager_aware_decorator():
    @context_manager_aware_decorator
    def print_before_and_after(func):
        @contextmanager
        def wrapper():
            print('before')
            with func() as x:
                yield x
            print('after')
        return wrapper

    @print_before_and_after
    @contextmanager
    def foo():
        print('yey')
        yield
        print('yo')

    with foo():
        print('hi')

    print('=' * 10)

    @print_before_and_after
    def bar():
        print('sup')

    bar()
