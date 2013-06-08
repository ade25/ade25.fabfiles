from cuisine import dir_ensure
from fabric.api import task, run, cd, env
from fabric.contrib.files import exists


def configure_egg_cache():
    """Configure a system-wide egg-cache so we have a local cache
    of eggs that we use in order to add speed and reduncancy to
    zc.buildout."""
    eggcache = '/opt/buildout-cache'

    dir_ensure(eggcache)
    dir_ensure('%s/{downloads,eggs,extends}' % eggcache)
    if exists('%s/default.cfg' % eggcache):
        run('rm -rf %s/default.cfg' % eggcache)

    run('touch %s/default.cfg' % eggcache)
    run('echo "[buildout]" >> /etc/buildout/default.cfg')
    run('echo "eggs-directory = %s/eggs" >> %s/default.cfg' % (eggcache, eggcache))
    run('echo "download-cache = /etc/buildout/downloads" >> /etc/buildout/default.cfg')
    run('echo "extends-cache = /etc/buildout/extends" >> /etc/buildout/default.cfg')

    # allow group `projects` to read/write in here
    run('chown -R root:projects /etc/buildout/{eggs,downloads,extends}')
    run('chmod -R 775 /etc/buildout/{eggs,downloads,extends}')

    # force maintenance users to also use default.cfg (needed when running buildout via Fabric)
    for user in env.admins:
        dir_ensure('/home/%s/.buildout' % user)
        if exists('/home/%s/.buildout/default.cfg' % user):
            run('rm -rf /home/%s/.buildout/default.cfg' % user)

        run('ln -s /etc/buildout/default.cfg /home/%s/.buildout/default.cfg' % user)
        run('chown -R %s /home/%s/.buildout' % (user, user))
