from cuisine import dir_ensure
from cuisine import user_ensure
from cuisine import group_ensure
from cuisine import group_user_ensure
from fabric.api import task, run, env, sudo, cd
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


@task
def set_project_user_and_group(username, groupname):
    """ Setup project user and group

        @param username: system user for zope process
        @param groupname: system process group for sites
    """
    user_ensure(username)
    group_ensure(groupname)
    group_user_ensure(groupname, username)


@task
def install_system_libs(additional_libs=None):
    """Install a bunch of stuff we need for normal operation such as
    ``gcc``, ``rsync``, ``vim``, ``libpng``, etc."""

    opts = dict(
        additional_libs=additional_libs or env.get('additional_libs') or '',
    )

    run('apt-get update')
    run('apt-get -yq install '
        # tools
        'sudo '
        'vim '
        'gitk '
        'lynx '
        'curl '
        'rsync '
        'unzip '
        'screen '
        'telnet '
        'build-essential '
        'python-software-properties '  # to get add-apt-repositories command
        'python-docutils '
        # imaging, fonts, compression, encryption, etc.
        'libbz2-dev '
        'libfreetype6-dev '
        'libjpeg-dev '
        'libldap-dev '
        'libpcre3-dev '
        'libreadline-dev '
        'libsasl2-dev '
        'libssl-dev '
        'libxml2-dev '
        'libxslt-dev '
        'libffi-dev '
        'pkg-config '
        'zlib1g-dev '
        'poppler-utils '
        'wv '
        '%(additional_libs)s' % opts
        )


@task
def install_python():
    """ Install Python """
    with cd('/opt'):
        run('wget https://bootstrap.pypa.io/get-pip.py')
        run('python get-pip.py')
        run('pip install virtualenv')
        run('git clone git@github.com:collective/buildout.python.git')
        with cd('/opt/buildout.python'):
            run('virtualenv .')
            run('bin/pip install zc.buildout')
            run('bin/buildout')


@task
def install_webserver():
    """ Install Python """
    run('git clone %s buildout.webserver' % (env.git_repo))
    run('cd buildout.webserver; ../bin/python bootstrap.py -c deployment.cfg')
    run('cd buildout.webserver; bin/buildout -c deployment.cfg')


@task
def setup_webserver_autostart():
    """ Install runlevel runscript for supervisord """
    with cd('/etc/init.d/'):
        run('ln -s %s/bin/runscript %s-supervisord' % (env.webserver,
            env.host))
        run('ln -s %s/bin/supervisorctl supervisorctl' % (env.webserver))
        run('update-rc.d %s-supervisord defaults' % (env.host))


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


@task
def configure_global_git_user(username=None, email=None):
    """ Setup global git user name for remote commits (needed for hotfixes)
    """
    opts = dict(
        username=username or env.get('git_username') or 'Christoph Boehner',
        email=email or env.get('email') or 'cb@vorwaerts-werbung.de'
    )
    run('git config --global user.name "%(username)s"' % opts)
    run('git config --global user.name "%(email)s"' % opts)


@task
def install_newrelic_monitor(newrelic_key=None):
    """ Install and configure New Relic sysmond Deamon

        @param key: the new relic licence key
    """
    opts = dict(
        newrelic_key=newrelic_key or env.get('newrelic_key') or ''
    )
    run('wget -O /etc/apt/sources.list.d/newrelic.list '
        'http://download.newrelic.com/debian/newrelic.list')
    run('wget -O- https://download.newrelic.com/548C16BF.gpg | apt-key add -')
    run('apt-get update')
    run('apt-get install newrelic-sysmond')
    run('nrsysmond-config --set license_key=%(newrelic_key)s' % opts)
    run('/etc/init.d/newrelic-sysmond start')
