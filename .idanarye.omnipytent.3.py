from omnipytent import *
from omnipytent.ext.idan import *

import os
import re


pytest = local['pyenv']['exec', 'py.test']


class PytestTest:
    COLLECT_ONLY_PATTERN = re.compile(r'''^\s*<(Package|Module|Function) ('.*'|".*")>$''', re.MULTILINE)
    def __init__(self, module, function):
        self.module = module
        self.function = function

    def __str__(self):
        return '%s::%s' % (self.module, self.function)

    @property
    def shortname(self):
        return '%s::%s' % (os.path.basename(self.module), self.function)

    @classmethod
    def find_at(cls, path):
        package = None
        module = None
        for m in cls.COLLECT_ONLY_PATTERN.finditer(pytest['--collect-only', path]()):
            kind, name = m.groups()
            name = name[1:-1]
            if kind == 'Package':
                package = name
                module = None
            elif kind == 'Module':
                if package:
                    module = os.path.join(package, name)
                else:
                    module = name
            else:
                assert kind == 'Function'
                yield cls(module=module, function=name)


@task.options_multi(alias=':1')
def choose_test(ctx):
    ctx.key(lambda test: test.shortname)
    yield from PytestTest.find_at('tests')


@task
def run(ctx, test=choose_test):
    # pytest['-qs']['tests/test_late_decorator.py'] & BANG
    # pytest['-qs']['tests/test_teams_lock.py'] & BANG
    # pytest['-qs']['tests/test_literate_assertions.py'] & BANG
    # pytest['-qs']['tests/test_versioning.py'] & BANG
    # pytest['-qs']['tests/test_construct_dsl.py'] & BANG
    # python3['-m', 'black_python_magic.gc_graph_tui'] & TERMINAL_PANEL.size(10)
    pytest['-qs'][test] & BANG


@task
def run_term(ctx, test=choose_test):
    # pytest['-qs']['tests/test_late_decorator.py'] & BANG
    # pytest['-qs']['tests/test_teams_lock.py'] & BANG
    # pytest['-qs']['tests/test_literate_assertions.py'] & BANG
    # pytest['-qs']['tests/test_versioning.py'] & BANG
    # pytest['-qs']['tests/test_construct_dsl.py'] & BANG
    # python3['-m', 'black_python_magic.gc_graph_tui'] & TERMINAL_PANEL.size(10)
    pytest['-qs'][test] & TERMINAL_TAB


@task
def act(ctx):
    pytest & BANG


@task
def explore(ctx):
    local['ipython3'] & TERMINAL_TAB


@task
def test_all(ctx):
    pytest['-qs']['tests'] & BANG


@task
def doc(ctx):
    local['rm']['-Rf', '_static', '_build'] & BANG
    local['sphinx-apidoc']['-o', '_static', 'black_python_magic'] & BANG
    # local['PYTHONPATH=`pwd`:$PYTHONPATH sphinx-build -M html "." "_build"
    try:
        python_path = os.environ['PYTHONPATH']
    except KeyError:
        python_path = str(local.path('.'))
    else:
        python_path = ':'.join([local.path('.'), python_path])
    local['sphinx-build']['-M', 'html', '.', '_build'].with_env(PYTHONPATH=python_path) & BANG
    local.path('_build/index.html').write("<meta http-equiv=refresh content=0;url=html/_static/black_python_magic.html>")


@task
def go(ctx):
    local['python2']['./test_python_2.py'] & BANG
