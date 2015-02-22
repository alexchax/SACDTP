from rpyc import *
import socket
from rpyc.utils.zerodeploy import DeployedServer
from plumbum import SshMachine

def getValue(key, conn):
    return conn.root.get(key)
def putValue(key, value, conn):
    return conn.root.put(key, value)


def main():
    mach = SshMachine("slice330.pcvm1-1.instageni.wisc.edu", user="root", keyfile=r"/id_rsa")
    server = DeployedServer(mach)
    try:
        conn = server.classic_connect()
    except socket.error:
        conn = connect("localhost", 18861)
    print putValue(15, 2, conn)
    print getValue(15, conn)

if __name__ == "__main__":
    main()
