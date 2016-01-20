#This file is part of trytontasks_tests. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import functools
import unittest
import time
import os
from invoke import task, run
from blessings import Terminal
from trytontasks_modules import read_config_file
from trytond.config import config

t = Terminal()

@task
def test(dbtype='sqlite', module=None):
    'Run Tryton test module/s'
    Modules = read_config_file()
    modules = Modules.sections()
    modules.sort()

    if module:
        if not module in modules:
            print "Not found  " + t.bold(module)
            return
        modules = [module]

    if dbtype == 'sqlite':
        configfile = 'sqlite.conf'
        database_name = ':memory:'
    else:
        configfile = 'trytond.conf'
        database_name = 'test_' + str(int(time.time()))

    if not os.path.exists(configfile):
        print "Not found  " + t.bold(configfile)
        return

    os.environ['DB_NAME'] = database_name

    import trytond.tests.test_tryton as test_tryton

    print "Run %s in %s database" % ('all' if len(modules) > 1 else module, database_name)

    config.update_etc(configfile)
    update_etc = functools.partial(config.update_etc, configfile)
    config.update_etc = lambda *args, **kwargd: update_etc()
    #~ config.update_etc(options)
    config.update_etc = lambda *args, **kwargs: None

    suite = test_tryton.modules_suite(modules=modules)
    text_runner = unittest.TextTestRunner().run(suite)
    print text_runner

@task
def pyflakes(module=None):
    'Run pyflakes in module/s'
    Modules = read_config_file()

    # remove base (trytond, tryton, proteus...)
    Bases = read_config_file('base.cfg')
    bases = Bases.sections()
    for base in bases: Modules.remove_section(base)

    modules = Modules.sections()
    modules.sort()

    if module:
        if not module in modules:
            print "Not found  " + t.bold(module)
            return
        modules = [module]

    for module in modules:
        path = '%s/%s' % (Modules.get(module, 'path'), module)
        files = []
        for f in sorted(os.listdir(path)):
            if f.endswith('.py') and f not in ['__init__.py', 'setup.py']:
                files.append('%s/%s' % (path, f))
        run('pyflakes %s' % ' '.join(files))
