from fabric.api import *


@task
def update():
    """ Update buildout from git/master """
    with cd(env.code_root):
        run('nice git pull')


@task
def build():
    """ Run buildout deployment profile """
    with cd(env.code_root):
        run('bin/buildout -Nc deployment.cfg')


@task
def build_full():
    """ Run buildout deployment profile and enforce updates """
    with cd(env.code_root):
        run('bin/buildout -c deployment.cfg')


@task
def restart():
    """ Restart instance """
    with cd(env.webserver):
        run('nice bin/supervisorctl restart instance-%(sitename)s' % env)
