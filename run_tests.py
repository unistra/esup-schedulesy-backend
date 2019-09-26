# -*- coding: utf-8 -*-


import os
import sys

import django
from django.apps import apps
from django.conf import settings
from django.test.utils import get_runner


def manage_model(model):
    model._meta.managed = True


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'schedulesy.settings.unittest'
    django.setup()
    test_apps = settings.LOCAL_APPS

    # Set all tested models to "managed = True"
    for app in test_apps:
        config = apps.get_app_config(app.split('.')[-1])
        list(map(manage_model, config.get_models()))

    test_apps = test_apps if len(sys.argv) <= 1 else sys.argv[1:]

    TestRunner = get_runner(settings)
    test_runner = TestRunner(pattern='test_*.py', verbosity=2,
                             interactive=True, failfast=False)
    failures = test_runner.run_tests(test_apps)
    sys.exit(failures)
