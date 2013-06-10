Introduction
============

This package holds fabricfiles that allow to run general administration tasks
from remote. The package consists of two main parts:

  * Server setup and configuration
  * Project and application management

Each hold further isolated tasks:

``` python
@task
def prepare_new_machine(self):
    execute(server.add_system_user())
```

These tasks are meant to be compiled into application specific common actions:

```python
from a25.fabfiles import project

@task
def deploy():
    """ Deploy current master to production server """
    project.site.update()
    project.site.restart()
```


Usage
=====

In order to make use of the provided recipes you neeed to generate a project
specific fabfile in your development buildout:

``` cfg
[fabric-build]
recipe=zc.recipe.egg
eggs=
    fabric
    ade25.fabfiles

[fabric-config]
recipe = collective.recipe.template
input = ${buildout:directory}/buildout.d/fabfile.py.in
output = ${buildout:directory}/fabfile.py
```

And provide a 'fabfile.py.in' template:

``` python
from fabric.api import task
from fabric.api import env

from ade25.fabfiles import project

env.use_ssh_config = True
env.forward_agent = True

```

After running your project buildout's development.cfg development profile you
should have the fab command. In order to display the available tasks and
actions:


``` bash
# bin/fab -list
Available commands:

    hotfix.update_package_list            Append package to buildout eggs
    project.db.backup                     Database backup
    project.db.download                   Database download
    project.db.fullbackup                 Database backup full
    project.db.restore                    Database backup restore
    project.db.snapshotbackup             Database backup snapshot
    project.site.build                    Buildout deployment profile (no update)
    project.site.build_full               Buildout deployment profile (full)
    project.site.restart                  Restart instance
    project.site.update                   Update buildout from git/master
    server.setup.configure_egg_cache      Configure a system-wide egg-cache for zc.buildout.
    server.setup.configure_fs             Configure filesystem structure
    server.setup.generate_selfsigned_ssl  Generate self-signed SSL certificates and provide them ...
    server.setup.generate_virtualenv      Configure virtualenv
    server.setup.install_python           Install Python
    server.status.disk                    Server disk and filesystem usage
    server.status.host_type               Server host type information
    server.status.load                    Server average system load
    server.status.memory                  Server memory usage
    server.status.status                  Server status information
    server.status.supervisor              Server supervisord process status
    server.status.uptime                  Server uptime
```

