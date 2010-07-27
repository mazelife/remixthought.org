#!/usr/bin/env python
# -*- coding: utf-8 -*-
# fabfile for Django:
# 
from __future__ import with_statement # needed for python 2.5
from fabric.api import *
from fabric.contrib.console import confirm

# globals
env.project_name = 'it_is'
env.user = 'asgood'
env.hosts = ['asgood.webfactional.com']
env.github_tarball = (
    'http://github.com/mazelife/remixthought.org/tarball/master'
)


###############################################################################
#                               Environments
###############################################################################

def staging():
    _webfaction()
    env.path = "%(base_path)s/it_is_staging/staging_env/" % env
    
def producton():
    _webfaction()
    env.path = "%(base_path)s/it_is_production/production_env/" % env

###############################################################################
#                                   Tasks    
###############################################################################

def test():
    """ Run project test suite."""
    with settings(warn_only=True):
        return local('python manage.py test statements', capture=False)
        #if result.failed and not confirm("Tests failed. Continue anyway?"):
        #    abort("Aborting at user request.")

def deploy():
    """
    Deploy the site on webfaction.
    
    #FIXME: this might be a little shell-scripty. But it works for now.
    """
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    env.github_checkout_name = 'it_is_master'
    with cd(env.path):
        # Get a tarball, unzip and rename.
        run('wget -q %(github_tarball)s' % env)
        archive_name = run((
            "find . -name 'mazelife*.tar.gz' | sed  's/\.tar\.gz//g'"
        ))
        run("find . -name 'mazelife*.tar.gz' -exec tar -xvzf {} \;")
        run("find . -name 'mazelife*.tar.gz' -exec rm {} \;")
        run("mv %s %s" % (archive_name, env.github_checkout_name))
        # Copy local settings into new project version.
        run((
            "cp %(project_name)s/local_settings.py %(github_checkout_name)s"
            "/%(project_name)s/"
        ) % env)
        # Archive the current project, restart apache.
        run("mv %(project_name)s %(release)s-%(project_name)s" % env)
        run("mv %(release)s-%(project_name)s archive/" %env)
        run("cp -r %(github_checkout_name)s/%(project_name)s ." % env)
        run("rm -r %(github_checkout_name)s" % env)
        run("sh ../apache2/bin/restart")
        
###############################################################################
#                               Helper Functions    
###############################################################################

def _webfaction():
    """ Some common webfaction settings."""
    env.user_name = 'asgood'
    env.base_path = '/home/%(user)s/webapps' % env