from collections import OrderedDict
from ConfigParser import ConfigParser

from fabric.api import env
from fabric.api import task


@task
def update_package_list(filename='packages.cfg', addon=None):
    """ Append package to buildout eggs

        @param filename: the configuration file to updated
        @param addon: the package name to append
    """
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
    print 'Egglist successfully updated'
