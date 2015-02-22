from rpyc import *
import socket
from rpyc.utils.zerodeploy import DeployedServer
from plumbum import SshMachine

def getValue(key, conn):
    return conn.root.get(key)
def putValue(key, value, conn):
    return conn.root.put(key, value)


def main():
    conn = connect("10.19.1.11", 18861)
    print putValue(52, 2, conn)
    print getValue(52, conn)

if __name__ == "__main__":
    main()
