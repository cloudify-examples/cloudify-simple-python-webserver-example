# Note, this contains some advanced info.

import os
import sys
import subprocess

# Import Cloudify's context object.
# This provides several useful functions as well as allowing to pass
# contextual information of an application.
from cloudify import ctx


IS_WIN = os.name == 'nt'
IS_DARWIN = (sys.platform == 'darwin')

# Get the port from the blueprint. We're running in the context of the
# `http_web_server` node so we can read its `port` property.
PORT = ctx.node.properties['port']


def run_server():
    webserver_cmd = [sys.executable, '-m', 'SimpleHTTPServer', str(PORT)]
    if not IS_WIN:
        webserver_cmd.insert(0, 'nohup')

    # The ctx object provides a built in logger.
    ctx.logger.info('Running WebServer locally on port: {0}'.format(PORT))
    # emulating /dev/null
    dn = open(os.devnull, 'wb')
    process = subprocess.Popen(webserver_cmd, stdout=dn, stderr=dn)

    # we need this for linux because on linux process.pid is not accurate.
    # it provides somewhat arbitrary values.
    if not IS_WIN and not IS_DARWIN:
        del webserver_cmd[0]
        get_pid = ['pidof', '-s']
        get_pid.extend(webserver_cmd)
        return int(subprocess.check_output(get_pid))
    else:
        return process.pid


def set_pid(pid):
    ctx.logger.info('Setting `pid` runtime property: {0}'.format(pid))
    # We can set runtime information in our context object which
    # can later be read somewhere in the context of the instance.
    # For instance, we want to save the `pid` here so that when we
    # run `uninstall.py`, we can destroy the process.
    ctx.instance.runtime_properties['pid'] = pid


pid = run_server()
set_pid(pid)
