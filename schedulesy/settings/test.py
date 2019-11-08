# -*- coding: utf-8 -*-

from os.path import normpath
from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


##########################
# Database configuration #
##########################

DATABASES['default']['HOST'] = '{{ default_db_host }}'
DATABASES['default']['USER'] = '{{ default_db_user }}'
DATABASES['default']['PASSWORD'] = '{{ default_db_password }}'
DATABASES['default']['NAME'] = '{{ default_db_name }}'

DATABASES['ade']['HOST'] = '{{ ade_db_host}}'
DATABASES['ade']['USER'] = '{{ ade_db_user }}'
DATABASES['ade']['PASSWORD'] = '{{ ade_db_password }}'
DATABASES['ade']['NAME'] = '{{ ade_db_name }}'


############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = [
    '.u-strasbg.fr',
    '.unistra.fr',
]


#############################
# Application configuration #
#############################

# Deactivate redis for tests
INSTALLED_APPS.remove('cacheops')


#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = '{{ remote_current_path }}/log/app.log'
LOGGING['handlers']['infocentre_file']['filename'] = '{{ remote_current_path }}/log/infocentre.log'

for logger in LOGGING['loggers']:
    LOGGING['loggers'][logger]['level'] = 'DEBUG'

LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'INFO',
}


################
# ADE settings #
################

ADE_WEB_API['USER'] = '{{ ade_ws_user }}'
ADE_WEB_API['PASSWORD'] = '{{ ade_ws_password }}'
ADE_WEB_API['HOST'] = '{{ ade_ws_host }}'
ADE_WEB_API['PROJECT_ID'] = '{{ ade_ws_project_id }}'

#########
# STAGE #
#########

STAGE = '{{ goal }}'

##########
# Sentry #
##########
sentry_init(STAGE)

######
# S3 #
######

AWS_ACCESS_KEY_ID = '{{ s3_access_key }}'
AWS_SECRET_ACCESS_KEY = '{{ s3_secret_key }}'
AWS_STORAGE_BUCKET_NAME = 'schedulesy_test'
AWS_S3_ENDPOINT_URL = '{{ s3_endpoint }}'


##########
# CELERY #
##########
RABBITMQ_USER = '{{ rabbitmq_user }}'
RABBITMQ_PASSWORD = '{{ rabbitmq_password }}'
RABBITMQ_SERVER = '{{ rabbitmq_server }}'
RABBITMQ_VHOST = '{{ rabbitmq_vhost }}'
BROKER_URL = "amqp://{}:{}@{}/".format(
    RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_SERVER, RABBITMQ_VHOST
)


###############################
# Weberservices configuration #
###############################

INFOCENTREWS_DESCRIPTION = 'https://rest-api-test2.u-strasbg.fr/infocentre/description.json'
INFOCENTREWS_BASE_URL = 'https://infocentrews-test.u-strasbg.fr'
INFOCENTREWS_TOKEN = '{{ infocentrews_token }}'

#########
# Redis #
#########
CACHEOPS_REDIS_SERVER = '{{ redis_server }}'
CACHEOPS_REDIS_PORT = int('{{ redis_port }}')
CACHEOPS_REDIS_DB = int('{{ redis_db }}')
CACHEOPS_REDIS = f'redis://{CACHEOPS_REDIS_SERVER}:{CACHEOPS_REDIS_PORT}/{CACHEOPS_REDIS_DB}'
