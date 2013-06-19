from collections import OrderedDict
from ConfigParser import ConfigParser

from cuisine import *
from fabric.api import env
from fabric.api import task
from fabric.api import cd
from fabric.api import run


@task
def process_hotfix(addon=None):
    """ Process hotfix for all hosted sites """
    for site in env.hosted_sites:
        apply_hotfix(
            sitename=site,
            addon=addon
        )
        print 'Processed hotfix for %s' % site


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
        path = '%s/%s/buildout.%s' % (env.host_root, site, site)
        with cd(site):
            run('nice git pull')
            cfg = file_read('packages.cfg')
            config_parser = ConfigParser(dict_type=OrderedDict)
            config_parser.read(cfg)
            import pdb; pdb.set_trace( )
            egglist = config_parser.get('eggs', 'addon')
            new_list = egglist + '\n%s' % addonpkg
            config_parser.set('eggs', 'addon', new_list)
            for x in config_parser.sections():
                for name, value in config_parser.items(x):
                    print '  %s = %r' % (name, value)
            with open(filename, 'wb') as configfile:
                config_parser.write(configfile)
            print 'Egglist for %s successfully updated' % site
            run('nice git add %s' % filename)
            commit = run('nice git commit -m "%s"' % msg)
            if commit.failed:
                print 'Could not commit changes'


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
