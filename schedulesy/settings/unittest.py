# -*- coding: utf-8 -*-

from os import environ
from os.path import normpath
import tempfile
from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


##########################
# Database configuration #
##########################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DEFAULT_DB_TEST_NAME', 'schedulesy'),
        'USER': environ.get('DEFAULT_DB_TEST_USER', 'schedulesy'),
        'PASSWORD': environ.get('DEFAULT_DB_TEST_PASSWORD', 'schedulesy'),
        'HOST': environ.get('DEFAULT_DB_TEST_HOST', 'postgres'),
        'PORT': environ.get('DEFAULT_DB_TEST_PORT', ''),
    }
}

DATABASE_ROUTERS = []

############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = [
    '*'
]


#############################
# Application configuration #
#############################

INSTALLED_APPS += [
    'schedulesy.libs.tests'
]

# Deactivate redis for tests
#INSTALLED_APPS.remove('cacheops')


#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = environ.get(
    'LOG_DIR', normpath(join('/tmp', f'test_{SITE_NAME}.log')))
LOGGING['handlers']['file']['level'] = 'DEBUG'

for logger in LOGGING['loggers']:
    LOGGING['loggers'][logger]['level'] = 'DEBUG'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = (
    'rest_framework.permissions.AllowAny',
)


################
# ADE settings #
################

ADE_WEB_API['USER'] = 'schedulesy'
ADE_WEB_API['PASSWORD'] = 'pass'
ADE_WEB_API['HOST'] = 'https://ade-test.unistra.fr/jsp/webapi'
ADE_WEB_API['PROJECT_ID'] = 5


###########
# Storage #
###########

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/unittest_media/'
MEDIA_ROOT = tempfile.mkdtemp()
