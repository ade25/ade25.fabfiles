from cuisine import dir_ensure
from fabric.api import task, run, env, sudo
from fabric.contrib.files import exists


# General error handler needed to catch misisng variables
def err(msg):
    raise AttributeError(msg)


@task
def configure_fs():
    """ Configure filesystem structure """
    dir_ensure('/opt/sites')


def set_hostname(server_ip=None, hostname=None):
    """Set server's hostname."""
    opts = dict(
        server_ip=server_ip or env.server_ip or err("env.server_ip missing"),
        hostname=hostname or env.hostname or err("env.hostname must be set"),
    )

    sudo('echo "\n%(server_ip)s %(hostname)s" >> /etc/hosts' % opts)
    sudo('echo "%(hostname)s" > /etc/hostname' % opts)
    sudo('hostname %(hostname)s' % opts)


def set_system_time(timezone=None):
    """Set timezone and install ``ntp`` to keep time accurate."""

    opts = dict(
        timezone=timezone or env.get('timezone') or '/usr/share/zoneinfo/UTC',
    )

    # set timezone
    sudo('cp %(timezone)s /etc/localtime' % opts)

    # install NTP
    sudo('apt-get -yq install ntp')


def install_system_libs(additional_libs=None):
    """Install a bunch of stuff we need for normal operation such as
    ``gcc``, ``rsync``, ``vim``, ``libpng``, etc."""

    opts = dict(
        additional_libs=additional_libs or env.get('additional_libs') or '',
    )

    run('apt-get update')
    run('apt-get -yq install '
        # tools
        'gitk '
        'lynx '
        'curl '
        'rsync '
        'unzip '
        'screen '
        'telnet '
        'build-essential '
        'python-software-properties '  # to get add-apt-repositories command

        # imaging, fonts, compression, encryption, etc.
        'libbz2-dev '
        'libfreetype6-dev '
        'libjpeg-dev '
        'libjpeg62-dev '
        'libldap-dev '
        'libpcre3-dev '
        'libreadline5-dev '
        'libsasl2-dev '
        'libssl-dev '
        'libxml2-dev '
        'libxslt-dev '
        'pkg-config '
        'zlib1g-dev '
        'poppler-utils '
        'wv '
        '%(additional_libs)s' % opts
        )


@task
def install_python():
    """ Install Python """
    # install Distribute
    # run('apt-get -yq install python2.6-dev')
    # run('curl -O http://python-distribute.org/distribute_setup.py')
    # run('python2.6 distribute_setup.py')
    # run('rm -f distribute*')
    # install buildout based python
    run('git clone git@github.com:collective/buildout.python.git')
    run('cd buildout.python; python bootstrap.py -d')
    run('cd buildout.python; bin/buildout')


@task
def generate_virtualenv(version='2.7', sitename=None):
    """ Configure virtualenv """
    run('buildout.python/bin/virtualenv-%s %s' % (version, sitename))


@task
def configure_egg_cache():
    """Configure a system-wide egg-cache for zc.buildout."""
    eggcache = '/opt/buildout-cache'

    dir_ensure(eggcache)
    dir_ensure('%s/downloads' % eggcache)
    dir_ensure('%s/eggs' % eggcache)
    dir_ensure('%s/extends' % eggcache)
    if exists('%s/default.cfg' % eggcache):
        run('rm -rf %s/default.cfg' % eggcache)

    run('touch %s/default.cfg' % eggcache)
    run('echo "[buildout]" >> /opt/buildout-cache/default.cfg')
    run('echo "eggs-directory = %s/eggs" >> %s/default.cfg' % (eggcache,
        eggcache))
    run('echo "download-cache = %s/downloads" >> %s/default.cfg' % (eggcache,
        eggcache))
    run('echo "extends-cache = %s/extends" >> %s/default.cfg' % (eggcache,
        eggcache))

    # allow group `www` to read/write in here
    run('chown -R root:www /opt/buildout-cache/{eggs,downloads,extends}')
    run('chmod -R 775 /opt/buildout-cache/{eggs,downloads,extends}')

    # force maintenance users to also use default.cfg
    # (needed when running buildout via Fabric)
    for user in env.admins:
        dir_ensure('/home/%s/.buildout' % user)
        if exists('/home/%s/.buildout/default.cfg' % user):
            run('rm -rf /home/%s/.buildout/default.cfg' % user)

        run('ln -s %s/default.cfg /home/%s/.buildout/default.cfg' % (eggcache,
            user))
        run('chown -R %s /home/%s/.buildout' % (user, user))


@task
def generate_selfsigned_ssl(hostname=None):
    """Generate self-signed SSL certificates and provide them to Nginx."""
    opts = dict(
        hostname=hostname or env.get('hostname') or 'STAR.ade25.de',
        webserver=env.get('webserver') or '/opt/webserver/buildout.webserver'
    )

    if not exists('mkdir etc/certs'):
        run('mkdir etc/certs')

    run('openssl genrsa -des3 -out server.key 2048')
    run('openssl req -new -key server.key -out server.csr')
    run('cp server.key server.key.password')
    run('openssl rsa -in server.key.password -out server.key')
    run('openssl x509 -req -days 365 '
        '-in server.csr -signkey server.key -out server.crt')
    run('cp server.crt %(webserver)s/etc/%(hostname)s.crt' % opts)
    run('cp server.key %(webserver)s/etc/%(hostname)s.key' % opts)
