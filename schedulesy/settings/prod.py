# -*- coding: utf-8 -*-

from os.path import normpath

from .base import *


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

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'ssl')


#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = '{{ remote_current_path }}/log/app.log'
LOGGING['handlers']['infocentre_file']['filename'] = '{{ remote_current_path }}/log/infocentre.log'

##############
# Secret key #
##############

SECRET_KEY = '{{ secret_key }}'


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
AWS_STORAGE_BUCKET_NAME = 'schedulesy'


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

INFOCENTREWS_DESCRIPTION = 'https://rest-api.u-strasbg.fr/infocentre/description.json'
INFOCENTREWS_BASE_URL = 'https://infocentre-ws.u-strasbg.fr'
INFOCENTREWS_TOKEN = '{{ infocentrews_token }}'
