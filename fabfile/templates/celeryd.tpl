####################
# General Settings #
####################
# Absolute or relative path to the 'celery' command:
# CELERY_BIN="/virtualenvs/def/bin/celery"
CELERY_BIN="{{ remote_virtualenv_dir }}/bin/celery"

# App instance to use
# comment out this line if you don't use an app
# or fully qualified: #CELERY_APP="proj.tasks:app"
CELERY_APP="{{ root_package_name }}"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1

DJANGO_SETTINGS_MODULE="{{ root_package_name }}.settings.{{ goal }}"

###################
# Worker Settings #
###################
# Names of nodes to start
#   most people will only start one node
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS (see `celery multi --help` for examples):
# CELERYD_NODES="worker1 worker2 worker3"
#   alternatively, you can specify the number of nodes to start:
# CELERYD_NODES=10
CELERYD_NODES="worker_{{ root_package_name }}"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %N will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%N.log"
CELERYD_PID_FILE="/var/run/celery/%N.pid"

# Where to chdir at start.
CELERYD_CHDIR="{{ remote_current_path }}"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists, e.g. nobody).
CELERYD_USER="django"
CELERYD_GROUP="di"

# Level of worker log (DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)
CELERYD_LOG_LEVEL="INFO"
