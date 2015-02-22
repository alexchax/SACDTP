import rpyc
import socket

def getDHT():
    DHT = {}
    filename = "DHT2.txt"
    try:
        with open(filename, "r") as DHTFile:
            for line in DHTFile:
                key, value = line.partition(":")[::2]
                DHT[int(key.strip())] = int(value.strip())
        return DHT
    except IOError:
        open(filename, 'a').close()


def updateDHT(DHT):
    print DHT
    with open("DHT2.txt", "w") as DHTFile:
        for key in DHT:
            DHTFile.write(str(key) + " : " + str(DHT[key]) + "\n")
        DHTFile.close()


class MyService(rpyc.Service):
    rpyc.Service.DHT = getDHT()
    rpyc.Service.node_id = 50
    rpyc.Service.neighbour_id = 0
    rpyc.Service.neighbour_ip = "localhost"
    rpyc.Service.conn = None
    rpyc.Service.neighbour_port = 18861
    try:
        rpyc.Service.conn = rpyc.connect(rpyc.Service.neighbour_ip, rpyc.Service.neighbour_port)
    except socket.error:
        pass
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_get(self, key):
        print key
        if rpyc.Service.node_id > rpyc.Service.neighbour_id or rpyc.Service.node_id < key < rpyc.Service.neighbour_id:
            print "found " + str(key)
            try:
                value = rpyc.Service.DHT[key]
            except KeyError:
                value = None
            return value
        else:
            if rpyc.Service.conn:
                print "next!"
                print "key: " + str(key)
                return rpyc.Service.conn.root.get(key)
            else:
                return None

    def exposed_put(self, key, value):
        if rpyc.Service.node_id < key < rpyc.Service.neighbour_id or rpyc.Service.node_id > rpyc.Service.neighbour_id:
            rpyc.Service.DHT[int(key)] = int(value)
            updateDHT(rpyc.Service.DHT)
            print str(key) + ":" + str(value) + " added to DHT"
            return True
        else:
            return rpyc.Service.conn.root.put(key, value)
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18862)
    t.start()