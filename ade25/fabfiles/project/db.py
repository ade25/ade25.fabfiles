from fabric.api import env
from fabric.api import task
from fabric.api import local
from fabric.api import get
from fabric.api import run
from fabric.api import cd
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.contrib import project


@task
def backup():
    """ Database backup """
    with cd(env.code_root):
        run('bin/backup')


@task
def fullbackup():
    """ Database backup full """
    with cd(env.code_root):
        run('bin/fullbackup')


@task
def snapshotbackup():
    """ Database backup snapshot """
    with cd(env.code_root):
        run('bin/backup')


@task
def restore():
    """ Database backup restore """
    with cd(env.code_root):
        run('bin/backup')


@task
def download(path=None):
    """ Database download """

    if not env.get('confirm'):
        confirm("This will destroy all current Zope data on your local "
                " machine. Are you sure you want to continue?")
    project.rsync_project(
        remote_dir='{0}/var/filestorage/Data.fs'.format(env.code_root),
        local_dir="./var/filestorage/",
        upload=False,
        exclude=['*.tmp', '*.index', '*.old', '*.lock']
        )
    project.rsync_project(
        remote_dir='{0}/var/blobstorage/'.format(env.code_root),
        local_dir="./var/blobstorage/",
        upload=False,
        exclude=['*.layout']
        )
