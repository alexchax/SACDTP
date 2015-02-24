from fabric.api import *
env.hosts = [
  "slice334.pcvm3-1.geni.case.edu",
      "slice334.pcvm3-1.instageni.metrodatacenter.com",
    "slice334.pcvm2-2.instageni.rnoc.gatech.edu",
    "slice334.pcvm3-2.instageni.illinois.edu",
    "slice334.pcvm5-7.lan.sdn.uky.edu",
    "slice334.pcvm3-1.instageni.lsu.edu",
    "slice334.pcvm2-2.instageni.maxgigapop.net",
    "slice334.pcvm1-1.instageni.iu.edu",
    "slice334.pcvm3-4.instageni.rnet.missouri.edu",
    "slice334.pcvm3-7.instageni.nps.edu",
    "slice334.pcvm2-1.instageni.nysernet.org",
    "slice334.pcvm3-11.genirack.nyu.edu",
    "slice334.pcvm5-1.instageni.northwestern.edu",
    "slice334.pcvm5-2.instageni.cs.princeton.edu",
    "slice334.pcvm3-3.instageni.rutgers.edu",
    "slice334.pcvm1-6.instageni.sox.net",
    "slice334.pcvm3-1.instageni.stanford.edu",
    "slice334.pcvm2-1.instageni.idre.ucla.edu",
    "slice334.pcvm4-1.utahddc.geniracks.net",
    "slice334.pcvm1-1.instageni.wisc.edu",
  ]
env.roledefs.update({
    'the_special': ["slice334.pcvm3-1.geni.case.edu"],
    'not_special': ["slice334.pcvm3-1.instageni.metrodatacenter.com",
    "slice334.pcvm2-2.instageni.rnoc.gatech.edu",
    "slice334.pcvm3-2.instageni.illinois.edu",
    "slice334.pcvm5-7.lan.sdn.uky.edu",
    "slice334.pcvm3-1.instageni.lsu.edu",
    "slice334.pcvm2-2.instageni.maxgigapop.net",
    "slice334.pcvm1-1.instageni.iu.edu",
    "slice334.pcvm3-4.instageni.rnet.missouri.edu",
    "slice334.pcvm3-7.instageni.nps.edu"],
})


env.key_filename="./id_rsa"
env.use_ssh_config = True
env.ssh_config_path = './ssh-config'

@parallel
def update_servers():
    put('server.py')
    put('main.py')
    run('rm DHT*')

@parallel
def setup_servers():
    put('server.py')
    put('main.py')
    run('apt-get update')
    run('apt-get install -y python-setuptools')
    run('apt-get install -y python-pip')
    run('sudo pip install rpyc')

@roles('the_special')
def run_server():
    run('python server.py ')

@roles('the_special')
def the_special():
    put('input.txt')
    run('python main.py input.txt')

@roles('not_special')
@parallel
def run_servers():
    run('python server.py 10.0.0.255')

def pingtest():
    run('ping -c 3 www.yahoo.com')

def uptime():
    run('uptime')
