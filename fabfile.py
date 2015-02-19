from fabric.api import env, run
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

env.key_filename="./id_rsa"
env.use_ssh_config = True
env.ssh_config_path = './ssh-config'

def pingtest():
    run('ping -c 3 www.yahoo.com')

def uptime():
    run('uptime')
