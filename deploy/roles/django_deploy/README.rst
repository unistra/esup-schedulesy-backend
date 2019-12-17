Django deploy
=============

Django application deployment with docker

Role Variables
--------------

Required Variables
++++++++++++++++++

- `django_deploy_app_name`: Application name in the docker containers
- `django_deploy_git_commit`

Optional Variables
++++++++++++++++++

- `django_deploy_web_server_envvars`: environment variables set in the web_server container
- `django_deploy_app_envvars`: environment variables set in the app container

Example Playbook
----------------

.. code:: yaml

    - hosts: server
      tasks:
        - include_role:
            name: django_deploy
          vars:
            django_deploy_app_name: myapp
            django_deploy_app_envvars:
              - POSTGRES_USER
              - POSTGRES_PASSWORD
              - POSTGRES_HOST
              - POSTGRES_PORT
              - POSTGRES_DB

License
-------

BSD

Author Information
------------------

dnum-dip@unistra.fr
