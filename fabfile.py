from fabric.api import *
env.hosts = [
  "slice315.pcvm3-1.geni.case.edu",
    "slice315.pcvm1-1.geni.it.cornell.edu",
    "slice315.pcvm3-1.instageni.metrodatacenter.com",
    "slice315.pcvm2-2.instageni.rnoc.gatech.edu",
    "slice315.pcvm3-2.instageni.illinois.edu",
    "slice315.pcvm5-7.lan.sdn.uky.edu",
    "slice315.pcvm3-1.instageni.lsu.edu",
    "slice315.pcvm2-2.instageni.maxgigapop.net",
    "slice315.pcvm1-1.instageni.iu.edu",
    "slice315.pcvm3-4.instageni.rnet.missouri.edu",
    "slice315.pcvm3-7.instageni.nps.edu",
    "slice315.pcvm2-1.instageni.nysernet.org",
    "slice315.pcvm3-11.genirack.nyu.edu",
    "slice315.pcvm5-1.instageni.northwestern.edu",
    "slice315.pcvm5-2.instageni.cs.princeton.edu",
    "slice315.pcvm3-3.instageni.rutgers.edu",
    "slice315.pcvm1-6.instageni.sox.net",
    "slice315.pcvm3-1.instageni.stanford.edu",
    "slice315.pcvm2-1.instageni.idre.ucla.edu",
    "slice315.pcvm4-1.utahddc.geniracks.net",
    "slice315.pcvm1-1.instageni.wisc.edu",
  ]
env.roledefs.update({
    'client' : ["slice315.pcvm3-1.geni.case.edu", "slice315.pcvm3-1.instageni.metrodatacenter.com", "slice315.pcvm2-2.instageni.rnoc.gatech.edu"]
})

env.key_filename="./id_rsa"
env.use_ssh_config = True
env.ssh_config_path = './ssh-config'

def pingtest():
    run('ping -c 3 www.yahoo.com')

@roles('client')
def iperf_client():
    run('iperf -c 10.1.0.234 -t 60 -f k -i 10 -f k ')

@roles('client')
@parallel
def pushtorrent():
    put('100M.txt.torrent')
    run("ip=$(ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')")
    run('time aria2c -q --seed-time=0 --bt-external-ip=$ip -T 100M.txt.torrent')
    run('rm 100M.txt*')

@roles('server')
def pulltorrent():
    get(remote_path='/var/www/html/100M.txt.torrent', local_path='./100M.txt.torrent')

@roles('client')
@parallel
def install_client():
    run('apt-get update')
    run('apt-get install -y aria2')

@roles('client')
@parallel
def script_client():
    run('cd /tmp')
    run('time aria2c -q http://10.1.0.234/100M.txt')
    run('ls -lah')
    run('yes | rm 100M.txt')

@roles('server')
def install_server():
    run('apt-get update')
    run('apt-get install -y apache2 bittorrent')

@roles('server')
def setup_server():
    run('python random.py')
    run('mv 100M.txt /var/www/html/')
    run('ls -lah /var/www/html')

@parallel
def uptime():
    run('uptime')
