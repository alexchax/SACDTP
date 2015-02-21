import rpyc


def getDHT():
    DHT = {}
    with open("DHT1.txt", "r") as DHTFile:
        for line in DHTFile:
            key, value = line.partition(":")[::2]
            DHT[key.strip()] = value.strip()
    return DHT


def updateDHT(DHT):
    open("DHT1.txt", "w").close()
    with open("DHT1.txt", "w") as DHTFile:
        for key in DHT:
            DHTFile.write(str(key) + " : " + str(DHT[key]) + "\n")


class MyService(rpyc.Service):
    rpyc.Service.DHT = getDHT()
    rpyc.Service.node_id = 10
    rpyc.Service.neighbour_id = 20

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_get(self, key):
        print key
        if rpyc.Service.node_id < key < rpyc.Service.neighbour_id:
            print "found " + str(key)
            return rpyc.Service.DHT[key]
        else:
            return 1

    def exposed_put(self, key, value):
        if rpyc.Service.node_id < key < rpyc.Service.neighbour_id:
            rpyc.Service.DHT[key] = value
            updateDHT(rpyc.Service.DHT)
            print str(key) + ":" + str(value) + " added to DHT"
            return True

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18861)
    t.start()