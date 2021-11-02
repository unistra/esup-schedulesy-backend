from fabric.api import env, sudo
from pydiploy.decorators import do_verbose


@do_verbose
def install():
    cmd = 'rabbitmqctl'
    user = env.application_name
    vhost = f'{env.application_name}_{env.goal}'

    user_exists = sudo(
        f'{cmd} list_users | grep {user}', warn_only=True
    )
    if user_exists.failed:
        sudo(f'{cmd} add_user {user} {env.rabbitmq_password}')
        sudo(f'{cmd} set_user_tags {user} management')

    vhost_exists = sudo(
        f'{cmd} list_vhosts | grep {vhost}', warn_only=True
    )

    if vhost_exists.failed:
        sudo(f'{cmd} add_vhost {vhost}')

    if vhost_exists.failed or user_exists.failed:
        sudo('{} set_permissions -p {} {} ".*" ".*" ".*"'.format(
            cmd, vhost, user
        ))

    guest_exists = sudo(
        f'{cmd} list_users | grep guest', warn_only=True
    )
    if guest_exists.succeeded:
        sudo(f'{cmd} delete_user guest')


@do_verbose
def enable_management():
    cmd = 'rabbitmq-plugins'
    plugin = 'rabbitmq_management'
    management_enabled = sudo(
        f'{cmd} list -e "^{plugin}$',
        warn_only=True
    )

    if management_enabled.failed:
        sudo(f'{cmd} enable {plugin}')
