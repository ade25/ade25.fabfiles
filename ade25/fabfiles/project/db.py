from fabric.api import env
from fabric.api import task
from fabric.api import local
from fabric.api import sudo
from fabric.api import get
from fabric.api import cd
from fabric.contrib.console import confirm
from fabric.contrib.files import exists


@task
def download_data():
    """ DB filestorage and blobstorage download """

    if not env.get('confirm'):
        confirm("This will destroy all current Zope data on your local "
                " machine. Are you sure you want to continue?")

    with cd(env.code_root):
        # remove temporary Data.fs file from previous downloads
        if exists('/tmp/Data.fs', use_sudo=True):
            sudo('rm -rf /tmp/Data.fs')
        # download Data.fs from server
        sudo('rsync -a filestorage/Data.fs /tmp/Data.fs')
        get('/tmp/Data.fs', '%(code_root)s/var/filestorage/Data.fs' % env)
        # remove temporary blobs from previous downloads
        if exists('/tmp/blobstorage', use_sudo=True):
            sudo('rm -rf /tmp/blobstorage')
        # download blobs from server
        sudo('rsync -a blobstorage /tmp/')
        sudo('chown -R %(user)s /tmp/blobstorage' % env)
        tmp_loc = '%(code_user)s@%(hostname)s:/tmp/blobstorage' % env
        path_bs = '%(code_root)s/var/' % env
        local('rsync -aPz %s %s' % (tmp_loc, path_bs))
