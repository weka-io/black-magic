from black_python_magic.gc_graph_tui import FORMAT_RULES, apply_format_rules

import gc


def test_format_rules():
    print()
    print('=' * 10)

    x = object()

    class Foo:
        def foo(self):
            return x


    Foo = Foo()

    for referrer in gc.get_referrers(x):
        print('referrer', referrer)
        print('formatted', apply_format_rules(referrer, FORMAT_RULES, None))

    print('=' * 10)
