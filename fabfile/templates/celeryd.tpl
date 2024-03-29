# Names of nodes to start
#   most people will only start one node:
CELERYD_NODES="worker_{{ root_package_name }}"
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS (see `celery multi --help` for examples):
#CELERYD_NODES="worker1 worker2 worker3"
#   alternatively, you can specify the number of nodes to start:
#CELERYD_NODES=10

export DJANGO_SETTINGS_MODULE="{{ root_package_name }}.settings.{{ goal }}"

# Absolute or relative path to the 'celery' command:
CELERY_BIN="{{ remote_virtualenv_dir }}/bin/celery" 
#CELERY_BIN="/virtualenvs/def/bin/celery"

# App instance to use
# comment out this line if you don't use an app
CELERY_APP="{{ root_package_name }}"
# or fully qualified:
#CELERY_APP="proj.tasks:app"

# Where to chdir at start.
CELERYD_CHDIR="{{ remote_current_path }}"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8 -B"

# %N will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%N.log"
CELERYD_PID_FILE="/var/run/celery/%N.pid"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists, e.g. nobody).
CELERYD_USER="django"
CELERYD_GROUP="di"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1
