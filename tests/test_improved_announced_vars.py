import black_python_magic.improved_announced_vars

from . import _logger


def test_improved_announced_vars():
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
