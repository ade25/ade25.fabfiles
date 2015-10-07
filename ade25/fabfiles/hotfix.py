from collections import OrderedDict
from ConfigParser import ConfigParser

from cuisine import *
from fabric.api import env
from fabric.api import task
from fabric.api import cd
from fabric.api import run
from fabric.api import local

from fabric.operations import get
from fabric.contrib.files import upload_template
from fabric.contrib.files import contains


@task
def close_firewall():
    """ Setup firewall and block everything but SSH and HTTP(S) """
    run('apt-get install ufw')
    run('ufw limit 22/tcp')
    run('ufw limit 22222/tcp')
    run('ufw allow 80/tcp')
    run('ufw allow 443/tcp')
    run('ufw enable')


@task
def process_hotfix(addon=None):
    """ Process hotfix for all hosted sites """
    idx = 0
    for site in env.hosted_sites:
        apply_hotfix(
            sitename=site,
            addon=addon
        )
        print 'Processed hotfix for %s' % site
        idx += 1
    print 'Hotfixed %s sites on %s' % (idx, env.hostname)


@task
def apply_hotfix(sitename=None, addon=None):
    """ Hotfix a single site/buildout """
    if sitename is None:
        print('A sitename is required')
    else:
        path = ('/opt/sites/%s/buildout.%s' % (sitename, sitename))
        with cd(path):
            run('bin/buildout -Nc deployment.cfg')


@task
def prepare_sites(addonpkg=None, filename='packages.cfg'):
    """ Add hotfix to eggs parts of all buildouts

        @param addon: Hotfix package name
        @param filename: configuration file to change
    """
    for site in env.site_locations:
        msg = 'Add %s' % addonpkg
        with cd(site):
            if contains('packages.cfg', addonpkg, exact=False):
                print '%s site already done' % site
            else:
                run('nice git pull')
                cfg = get('packages.cfg', 'hotfix.cfg')
                config_parser = ConfigParser(dict_type=OrderedDict)
                config_parser.read(cfg)
                egglist = config_parser.get('eggs', 'addon')
                new_list = egglist + '\n%s' % addonpkg
                config_parser.set('eggs', 'addon', new_list)
                #for x in config_parser.sections():
                #    for name, value in config_parser.items(x):
                #        print '  %s = %r' % (name, value)
                with open('hotfix.cfg', 'wb') as configfile:
                    config_parser.write(configfile)
                upload_template('hotfix.cfg', filename, backup=False)
                local('rm hotfix.cfg')
                run('nice git add %s' % filename)
                commit = run('nice git commit -m \"%s\"' % msg)
                if commit.failed:
                    print 'Could not commit changes to %s' % site
                else:
                    run('nice git push')
                    print 'Egglist for %s successfully updated' % site


@task
def update_package_list(filename='packages.cfg', addon=None, site='Plone'):
    """ Append package to buildout eggs

        @param filename: the configuration file to update
        @param addon: the package name to append
        @param site: name of the site to be updated
    """
    if addon is None:
        print('Please provide an addon name')
    else:
        cfgfile = '%s/%s' % (site, filename)
        print 'Processing %s in %s' % (filename, site)
        config_parser = ConfigParser(dict_type=OrderedDict)
        config_parser.read(cfgfile)
        egglist = config_parser.get('eggs', 'addon')
        new_list = egglist + '\n%s' % addon
        config_parser.set('eggs', 'addon', new_list)
        for x in config_parser.sections():
            for name, value in config_parser.items(x):
                print '  %s = %r' % (name, value)
        with open(filename, 'wb') as configfile:
            config_parser.write(configfile)
        print 'Egglist for %s successfully updated' % site
