
from __future__ import print_function

from fabric.api import *
from fabric.contrib.files import *
from fabric.utils import *

from hetzner import HetznerRobot
from poll import poll,up

import socket,time

from pprint import pprint as pp

env.shell = "/bin/sh -c"
env.robot_user,env.robot_pw,env.ip = [ x.strip() for x in open("/Users/paulc/.hetzner").readlines() ]


def wait_reboot():
    logf = lambda : fastprint(".")

    puts("Waiting for shutdown",end="")
    fastprint("")
    up(env.host,22,logf)
    fastprint("\n")

    puts("Waiting for reboot",end="")
    fastprint("")
    poll(env.host,22,600,logf)
    fastprint("\n")

@task
def connect():
    with settings(disable_known_hosts=True):
        prompt("Password:",key='password')
        open_shell()

@task
def reset(os='freebsd',arch='64'):
    robot = HetznerRobot(env.robot_user,env.robot_pw)
    server = robot.server(socket.gethostbyname(env.host))
    server.rescue(delete=True)
    server.reset()
    wait_reboot()

@task
def rescue(os='freebsd',arch='64',shell=True):

    robot = HetznerRobot(env.robot_user,env.robot_pw)
    server = robot.server(socket.gethostbyname(env.host))

    server.rescue(delete=True)
    status = server.rescue('freebsd',64)
    if not status['active']:
        error("Could not activate rescue system")
    puts("Rescue system activated - pw: %s" % status['password'])

    try:
        puts("Trying to shutdown")
        with settings(connection_attempts=1):
            run("shutdown -r now",pty=False,timeout=5)
    except:
        puts("Shutdown failed - sending hardware reset")
        server.reset()

    wait_reboot()

    if shell:
        time.sleep(5)
        with settings(disable_known_hosts=True):
            env.password = str(status['password'])
            open_shell()

@task
def update():
    run("freebsd-update fetch")
    run("freebsd-update install")

@task
def info():
    run("hostname")
    run("uname -a")
    run("uptime")
    run("sysrc -a")

@task
def report():
    hostname = run("hostname")
    uname = run("uname -a")
    uptime = run("uptime")
    rcconf = run("sysrc -a")
    upload_template("info.tpl","report.txt",context=locals())

