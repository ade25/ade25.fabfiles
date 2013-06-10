from fabric.api import cd
from fabric.api import task
from fabric.api import env
from fabric.api import run


@task
def restart_custer():
    with cd(env.webserver):
        for site in env.sites:
            run('nice bin/supervisorctl restart instance-%s' % site)
