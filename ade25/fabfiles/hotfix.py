from collections import OrderedDict
from ConfigParser import ConfigParser

from fabric.api import env
from fabric.api import task
from fabric.api import cd
from fabric.api import run


@task
def process_hotfix(addon=None):
    """ Process hotefix for all hosted sites """
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
def prepare_sites(addon=None, filename='packages.cfg'):
    """ Prepare each hosted site by updating the buildout configuration """
    msg = 'Add %s to %s' % (addon, filename)
    for site in env.hosted_sites:
        run('nice git pull')
        update_package_list(
            filename=filename,
            addon=addon,
            site=site
        )
        run('nice git add %s' % filename)
        run('nice git commit -m %s' % msg)


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
        filename = '%s/%s' % (env.local_root, filename)
        config_parser = ConfigParser(dict_type=OrderedDict)
        config_parser.read(filename)
        egglist = config_parser.get('eggs', 'addon')
        new_list = egglist + '\n%s' % addon
        config_parser.set('eggs', 'addon', new_list)
        for x in config_parser.sections():
            for name, value in config_parser.items(x):
                print '  %s = %r' % (name, value)
        with open(filename, 'wb') as configfile:
            config_parser.write(configfile)
        print 'Egglist for %s successfully updated' % site
