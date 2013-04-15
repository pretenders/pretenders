from fabric.api import task, put, run, get, local
from fabric.contrib.project import rsync_project


#DAEMON = '~/init/wishlist'
LIGHTTPD = '~/init/lighttpd'
LIGHTTPD_CONF = '~/lighttpd/pretenders.conf'
SRV_HOME = '~/srv/pretenders'
ENV_HOME = '~/env/pretenders'
PYTHON = ENV_HOME + '/bin/python'
# MANAGE = '{0} {1}'.format(PYTHON, SRV_HOME + '/manage.py')


@task
def deploy():
    """Copy project to txels.com"""
    rsync_project(
        local_dir='.',
        remote_dir=SRV_HOME,
        exclude=['test', '.*', '*~', '*.pyc'],
        extra_opts='--omit-dir-times')
    put('deploy/lighttpd.pretenders', LIGHTTPD_CONF)
    run(LIGHTTPD + ' restart')
