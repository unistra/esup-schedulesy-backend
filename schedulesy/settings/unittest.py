# -*- coding: utf-8 -*-
import uuid
from datetime import timedelta
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

LOGGING['handlers'].pop('logstash')
LOGGING['loggers'].pop('schedulesy')

DATABASE_ROUTERS = []

############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = [
    '*'
]


############################
# Middleware configuration #
############################

MIDDLEWARE.remove('schedulesy.middleware.StatsMiddleware')


#############################
# Application configuration #
#############################

INSTALLED_APPS += [
    'schedulesy.libs.tests'
]

# Deactivate redis for tests
INSTALLED_APPS.remove('cacheops')


#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = environ.get(
    'LOG_DIR', normpath(join('/tmp', f'test_{SITE_NAME}.log')))
LOGGING['handlers']['infocentre_file']['filename'] = environ.get(
    'LOG_DIR', normpath(join('/tmp', f'test_infocentre_{SITE_NAME}.log')))

for logger in LOGGING['loggers']:
    LOGGING['loggers'][logger]['level'] = 'ERROR'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = (
    'rest_framework.permissions.AllowAny',
)
REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'


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


###############################
# Weberservices configuration #
###############################

INFOCENTREWS_DESCRIPTION = join(
    DJANGO_ROOT, 'libs', 'api', 'tests', 'description_infocentre.json')
INFOCENTREWS_BASE_URL = 'https://infocentrews-test.u-strasbg.fr'
INFOCENTREWS_TOKEN = 'TOK3N'

SIMPLE_JWT = {
    'USER_ID_FIELD': 'username',
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': str(uuid.uuid4()),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

}
