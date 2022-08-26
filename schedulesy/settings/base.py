# -*- coding: utf-8 -*-

from os.path import abspath, basename, dirname, join, normpath, isfile

######################
# Path configuration #
######################
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)


#######################
# Debug configuration #
#######################

DEBUG = False
TEMPLATE_DEBUG = DEBUG


##########################
# Manager configurations #
##########################

ADMINS = [
    # ('Your Name', 'your_email@example.com'),
]

MANAGERS = ADMINS


##########################
# Database configuration #
##########################

# In your virtualenv, edit the file $VIRTUAL_ENV/bin/postactivate and set
# properly the environnement variable defined in this file (ie: os.environ[KEY])
# ex: export DEFAULT_DB_USER='schedulesy'

# Default values for default database are :
# engine : sqlite3
# name : PROJECT_ROOT_DIR/schedulesy.db

# defaut db connection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'schedulesy',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    },
    'ade': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ade',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    }
}

DATABASE_ROUTERS = ['schedulesy.db_router.DBRouter']
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


######################
# Site configuration #
######################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []


#########################
# General configuration #
#########################

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


#######################
# locale configuration #
#######################

LOCALE_PATHS = [
    normpath(join(DJANGO_ROOT, 'locale')),
]


#######################
# Media configuration #
#######################

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'


##############################
# Static files configuration #
##############################

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/site_media/'

# Additional locations of static files
STATICFILES_DIRS = [
    normpath(join(DJANGO_ROOT, 'static')),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


##############
# Secret key #
##############

# Make this unique, and don't share it with anybody.
# Only for dev and test environnement. Should be redefined for production
# environnement
SECRET_KEY = 'ma8r116)33!-#pty4!sht8tsa(1bfe%(+!&9xfack+2e9alah!'


##########################
# Template configuration #
##########################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]


############################
# Middleware configuration #
############################

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'schedulesy.middleware.StatsMiddleware',
    'django_cas.middleware.CASMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


#####################
# Url configuration #
#####################

ROOT_URLCONF = '%s.urls' % SITE_NAME


######################
# WSGI configuration #
######################

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME


#############################
# Application configuration #
#############################

DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # 'django.contrib.admindocs',
]

THIRD_PARTY_APPS = [
    'django_cas',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'cacheops',
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
    'health_check.contrib.migrations',
    'health_check.contrib.s3boto3_storage',  # requires boto3 and S3BotoStorage backend
    'health_check.contrib.rabbitmq',  # requires RabbitMQ broker
    'health_check.contrib.redis',
]

LOCAL_APPS = [
    'schedulesy',
    'schedulesy.apps.ade_api',
    'schedulesy.apps.ade_legacy.apps.AdeLegacyConfig',
    'schedulesy.apps.refresh',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


#########################
# Session configuration #
#########################

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

#####################
# Log configuration #
#####################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)s %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '',
            'maxBytes': 209715200,
            'backupCount': 3,
            'formatter': 'default'
        },
        'infocentre_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '',
            'maxBytes': 209715200,
            'backupCount': 3,
            'formatter': 'default'
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'version': 1,
            'message_type': 'logstash',
            'fqdn': True,
            'tags': ['schedulesy'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'schedulesy': {
            'handlers': ['logstash'],
            'level': 'INFO',
            'propagate': True
        },
        'infocentre': {
            'handlers': ['infocentre_file'],
            'level': 'ERROR',
            'propagate': True
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'schedulesy.libs.authentication.CustomJWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

}

AUTHENTICATION_BACKENDS = (
    'django_cas.backends.CASBackend',
    'django.contrib.auth.backends.ModelBackend',
)


################
# ADE settings #
################

ADE_WEB_API = {
    'USER': '',
    'PASSWORD': '',
    'HOST': ''
}
ADE_DEFAULT_TIMEZONE = 'Europe/Paris'
ADE_DEFAULT_DURATION = 15
ADE_MAX_EVENTS = 7000  # Max events per customization


########
# CAS #
########

CAS_SERVER_URL = "https://cas.unistra.fr:443/cas/login"
CAS_LOGOUT_COMPLETELY = True
CAS_LOGOUT_REQUEST_ALLOWED = ('cas1.di.unistra.fr', 'cas2.di.unistra.fr')
CAS_USER_CREATION = True
CAS_ADMIN_AUTH = True
#CAS_CUSTOM_FORBIDDEN = 'forbidden-view'
CAS_USERNAME_FORMAT = lambda username: username.lower().strip()

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = ('http://localhost:8080',)

CORS_ALLOW_CREDENTIALS = True

SIMPLE_JWT = {
    'USER_ID_FIELD': 'username',
    'ALGORITHM': 'RS256',
    'CREATE_USER': True,  # CustomJWTAuthentication parameter
}


def check_key(filename, key_type):
    full_path = join(SITE_ROOT, "keys", filename)
    if isfile(full_path):
        SIMPLE_JWT[key_type] = open(full_path, 'rb').read()


check_key('myPublic.pem', 'VERIFYING_KEY')


##########
# Sentry #
##########
def sentry_init(environment):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from os import path

    sentry_sdk.init(
        dsn="https://2ab6b76118c54c5a982d095a1c9cdcc2@sentry.app.unistra.fr/5",
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        environment=environment,
        release=open(path.join(SITE_ROOT, "build.txt")).read()
    )


##########
# CELERY #
##########

CELERY_NAME = "schedulesy"
CELERY_RESULT_BACKEND = ''
CELERY_RESULT_PERSISTENT = False
BROKER_URL = ""
# minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
# WARNING : use London TZ
REFRESH_SCHEDULE = {'minute': 0, 'hour': 2}


######
# S3 #
######

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=3600',
}
ICS_EXPIRATION = 3600

#########
# STAGE #
#########

STAGE = None

#########
# Redis #
#########
CACHEOPS_DEFAULTS = {
    'timeout': 60*15
}
CACHEOPS = {
    'ade_api.*': {'ops': 'all'},
    '*.*': {},
}
