from fabric.api import env
from fabric.api import task
from fabric.api import local
from fabric.api import get
from fabric.api import run
from fabric.api import cd
from fabric.contrib.console import confirm
from fabric.contrib.files import exists


@task
def backup():
    """ Database backup """
    with cd(env.code_root):
        run('bin/backup')


@task
def fullbackup():
    """ Database backup full """
    with cd(env.code_root):
        run('bin/backup')


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
def download():
    """ Database download """

    if not env.get('confirm'):
        confirm("This will destroy all current Zope data on your local "
                " machine. Are you sure you want to continue?")

    with cd(env.code_root):
        # remove temporary Data.fs file from previous downloads
        if exists('/tmp/Data.fs', use_sudo=True):
            run('rm -rf /tmp/Data.fs')
        # download Data.fs from server
        run('rsync -a filestorage/Data.fs /tmp/Data.fs')
        get('/tmp/Data.fs', '%(code_root)s/var/filestorage/Data.fs' % env)
        # remove temporary blobs from previous downloads
        if exists('/tmp/blobstorage', use_sudo=True):
            run('rm -rf /tmp/blobstorage')
        # download blobs from server
        run('rsync -a blobstorage /tmp/')
        run('chown -R %(user)s /tmp/blobstorage' % env)
        tmp_loc = '%(code_user)s@%(hostname)s:/tmp/blobstorage' % env
        path_bs = '%(code_root)s/var/' % env
        local('rsync -aPz %s %s' % (tmp_loc, path_bs))
