Introduction
============

This package holds fabricfiles that allow to run general administration tasks
from remote. The package consists of severl submodules:

  * server
  * site
  * app

Each will eventuall hold further isolated submodules that perform specific
tasks:

``` python
from ade25.fabfiles import server

@task
def prepare_new_machine(self):
    execute(server.add_system_user())
```

