from fabric.api import cd
from fabric.api import task
from fabric.api import env
from fabric.api import run


@task
def restart_all():
    """ Restart all """
    with cd(env.webserver):
        run('nice bin/supervisorctl restart all')


@task
def restart_nginx():
    """ Restart all """
    with cd(env.webserver):
        run('nice bin/supervisorctl restart nginx')


@task
def restart_varnish():
    """ Restart all """
    with cd(env.webserver):
        run('nice bin/supervisorctl restart varnish')


@task
def restart_haproxy():
    """ Restart all """
    with cd(env.webserver):
        run('nice bin/supervisorctl restart haproxy')


@task
def reload_supervisor():
    """ Reload supervisor configuration """
    with cd(env.webserver):
        run('bin/supervisorctl reread')
        run('bin/supervisorctl update')
