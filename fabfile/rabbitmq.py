from fabric.api import env, sudo
from pydiploy.decorators import do_verbose


@do_verbose
def install():
    cmd = 'rabbitmqctl'
    user = env.application_name
    vhost = '{}_{}'.format(env.application_name, env.goal)

    user_exists = sudo(
        '{} list_users | grep {}'.format(cmd, user), warn_only=True
    )
    if user_exists.failed:
        sudo('{} add_user {} {}'.format(cmd, user, env.rabbitmq_password))
        sudo('{} set_user_tags {} management'.format(cmd, user))

    vhost_exists = sudo(
        '{} list_vhosts | grep {}'.format(cmd, vhost), warn_only=True
    )

    if vhost_exists.failed:
        sudo('{} add_vhost {}'.format(cmd, vhost))

    if vhost_exists.failed or user_exists.failed:
        sudo('{} set_permissions -p {} {} ".*" ".*" ".*"'.format(
            cmd, vhost, user
        ))

    guest_exists = sudo(
        '{} list_users | grep guest'.format(cmd), warn_only=True
    )
    if guest_exists.succeeded:
        sudo('{} delete_user guest'.format(cmd))


@do_verbose
def enable_management():
    cmd = 'rabbitmq-plugins'
    plugin = 'rabbitmq_management'
    management_enabled = sudo(
        '{} list -e "^{}$'.format(cmd, plugin),
        warn_only=True
    )

    if management_enabled.failed:
        sudo('{} enable {}'.format(cmd, plugin))
