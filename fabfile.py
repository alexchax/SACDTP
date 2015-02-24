from fabric.api import *
env.hosts = [
  "slice330.pcvm3-1.geni.case.edu",
      "slice330.pcvm3-1.instageni.metrodatacenter.com",
    "slice330.pcvm2-2.instageni.rnoc.gatech.edu",
    "slice330.pcvm3-2.instageni.illinois.edu",
    "slice330.pcvm5-7.lan.sdn.uky.edu",
    "slice330.pcvm3-1.instageni.lsu.edu",
    "slice330.pcvm2-2.instageni.maxgigapop.net",
    "slice330.pcvm1-1.instageni.iu.edu",
    "slice330.pcvm3-4.instageni.rnet.missouri.edu",
    "slice330.pcvm3-7.instageni.nps.edu",
    "slice330.pcvm2-1.instageni.nysernet.org",
    "slice330.pcvm3-11.genirack.nyu.edu",
    "slice330.pcvm5-1.instageni.northwestern.edu",
    "slice330.pcvm5-2.instageni.cs.princeton.edu",
    "slice330.pcvm3-3.instageni.rutgers.edu",
    "slice330.pcvm1-6.instageni.sox.net",
    "slice330.pcvm3-1.instageni.stanford.edu",
    "slice330.pcvm2-1.instageni.idre.ucla.edu",
    "slice330.pcvm4-1.utahddc.geniracks.net",
    "slice330.pcvm1-1.instageni.wisc.edu",
  ]
env.roledefs.update({
    'the_special': ["slice330.pcvm3-1.geni.case.edu"],
    'not_special': ["slice330.pcvm3-1.instageni.metrodatacenter.com"],
    'not_special1': ["slice330.pcvm3-1.instageni.lsu.edu"],
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
    run('python main.py')
    run('put 23 5')
    run('put 1 4')
    run('put 525 3')

@roles('not_special')
@parallel
def run_servers():
    run('python server.py 10.0.0.255')

@roles('not_special1')
def runservers():
    run('python server.py 10.0.0.255')

def uptime():
    run('ifconfig')
