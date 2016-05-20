# -*- coding: utf-8 -*-
"""Module providing database management tasks"""
from fabric.api import env
from fabric.api import task
from fabric.api import run
from fabric.api import cd
from fabric.contrib.console import confirm
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
def zipbackup():
    """ Database backup zipped """
    with cd(env.code_root):
        run('bin/zipbackup')


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


@task
def download_backup(path=None):
    """ Database backup download """
    project.rsync_project(
        remote_dir='/opt/backups/{0}/zipbackups/*'.format(env.sitename),
        local_dir="./var/zipbackups",
        upload=False,
        exclude=['*.tmp', '*.old', '*.lock']
    )
    project.rsync_project(
        remote_dir='/opt/backups/{0}/backups/blobzip/*'.format(env.sitename),
        local_dir="./var/zipblobbackups",
        upload=False,
        exclude=['*.layout']
    )


@task
def get_secrets():
    """  Download secrets.cfg from production environment """
    project.rsync_project(
        remote_dir='{0}/secret.cfg'.format(env.code_root),
        local_dir="./secret.cfg",
        upload=False,
    )
