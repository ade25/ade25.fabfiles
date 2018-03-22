# -*- coding: utf-8 -*-
"""Module providing docker compose commands"""
from fabric import api
from fabric.api import task


@task
def build():
    """ Build docker container """
    build_dir = '{0}/build'.format(api.env.local_root)
    configuration = '-f docker-compose.yml -f docker-compose.traefik.yml'
    with api.lcd(build_dir):
        api.local('docker-compose {0} build'.format(configuration))


@task
def run():
    """ Run docker container """
    build_dir = '{0}/build'.format(api.env.local_root)
    configuration = '-f docker-compose.yml -f docker-compose.traefik.yml'
    with api.lcd(build_dir):
        api.local('docker-compose {0} up'.format(configuration))
