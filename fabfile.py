from fabric.api import task, put, run, get, local
from fabric.contrib.project import rsync_project


LIGHTTPD = '~/init/lighttpd'
LIGHTTPD_CONF = '~/lighttpd/pretenders.conf'
SRV_HOME = '~/srv/pretenders'
ENV_HOME = '~/env/pretenders'
PYTHON = ENV_HOME + '/bin/python'


@task
def deploy():
    """
    Deploy to remote server and restart.
    """
    rsync_project(
        local_dir='.',
        remote_dir=SRV_HOME,
        exclude=['test', '.*', '*~', '*.pyc'],
        extra_opts='--omit-dir-times')
    put('deploy/lighttpd.pretenders', LIGHTTPD_CONF)
    run(LIGHTTPD + ' restart')
