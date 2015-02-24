import rpyc
import socket
import sys


def getDHT():
    # pulls all values from a textfile and puts them into a DHT
    DHT = {}
    filename = "DHT.txt"
    try:
        with open(filename, "r") as DHTFile:
            for line in DHTFile:
                key, value = line.partition(":")[::2]
                DHT[int(key.strip())] = int(value.strip())
        return DHT
    except IOError:
        open(filename, 'a').close()
        return DHT


def updateDHT(DHT):
    # writes the current DHT into a file (key) : (value)
    with open("DHT.txt", "w") as DHTFile:
        for key in DHT:
            DHTFile.write(str(key) + " : " + str(DHT[key]) + "\n")
        DHTFile.close()

class Node:
    def __init__(self):
        self.neighbour_ip = None
        self.DHT = {}
        self.Max = 1000000
        self.node_id = None
        self.node_ip = None
        self.node_port = 18861
        self.neighbour_id = None
        self.neighbour_port = 18861
        self.conn = None


class MyService(rpyc.Service):
    rpyc.Service.node = Node()
    rpyc.Service.node.neighbour_ip = socket.gethostbyname(socket.gethostname())
    # arg(1) - ip of the node you want to connect to
    if len(sys.argv) == 2:
        rpyc.Service.node.neighbour_ip = sys.argv[1]
    if len(sys.argv) == 3:
        rpyc.Service.node.neighbour_ip = sys.argv[1]
        rpyc.Service.node.node_port = sys.argv[2]
    rpyc.Service.node.DHT = getDHT()
    print rpyc.Service.node.DHT
    # maximum number of values in the DHT's
    rpyc.Service.node.Max = 1000000
    rpyc.Service.node.pointer = rpyc.Service.node.DHT
    # node id - index of first value in current DHT
    rpyc.Service.node.node_id = 0
    # ip of the current node
    rpyc.Service.node.node_ip = socket.gethostbyname(socket.gethostname())
    # neighbour id - the id of the next node in the DHT
    rpyc.Service.node.neighbour_id = rpyc.Service.node.Max
    # port that the server is running on - always 18861
    rpyc.Service.node.neighbour_port = 18861

    print "connecting to: " + str(rpyc.Service.node.neighbour_ip)
    try:
        # try connecting to the server put in the args
        # setup connection using rpyc
        rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
        # uses the inital connection method to split up the DHT
        rpyc.Service.node.node_id, rpyc.Service.node.neighbour_id, rpyc.Service.node.DHT, rpyc.Service.node.neighbour_ip = rpyc.Service.node.conn.root.connect(rpyc.Service.node.node_ip)
        # debug statement
        print str(rpyc.Service.node.node_id) + " " + str(rpyc.Service.node.neighbour_id) + " " + str(rpyc.Service.node.DHT) + " " + str(rpyc.Service.node.neighbour_ip) + " " + str(rpyc.Service.node.node_ip)
        updateDHT(rpyc.Service.node.DHT)
        print "connection between: " + rpyc.Service.node.node_ip + " and " + rpyc.Service.node.neighbour_ip + " established"
    except socket.error:
        # if arg not set or connection is unable to be set dont connect to the DHT
        print "connection not found"
    print rpyc.Service.node.node_ip
    # "exposed_-" allows other nodes to use a connection to call these functions
    def exposed_connect(self, node_ip):
        # connects a node to the Chord Scheme
        print "connected to: " + node_ip

        # if the current node is the only one in the Chord Scheme use this
        if rpyc.Service.node.node_id == 0 and rpyc.Service.node.neighbour_id == rpyc.Service.node.Max:
            print "there"
            middle_id = rpyc.Service.node.Max/2
            top_DHT = {}
            bottom_DHT = {}
            for key in rpyc.Service.node.DHT:
                if key > middle_id:
                    top_DHT[key] = rpyc.Service.node.DHT[key]
                else:
                    bottom_DHT[key] = rpyc.Service.node.DHT[key]
            rpyc.Service.node.DHT = bottom_DHT
            rpyc.Service.node.neighbour_id = middle_id
            updateDHT(bottom_DHT)
            rpyc.Service.node.neighbour_ip = node_ip
            return middle_id, 0, top_DHT, rpyc.Service.node.node_ip
        else:
            # if current node is not the node connected to the "start" node
            if rpyc.Service.node.neighbour_id > rpyc.Service.node.node_id:
                print "here"
                middle_id = (rpyc.Service.node.neighbour_id - rpyc.Service.node.node_id)/2 + rpyc.Service.node.node_id
                n_id = rpyc.Service.node.neighbour_id
                rpyc.Service.node.neighbour_id = middle_id
            # if current node is the last in the chord
            else:
                print "here2"
                middle_id = round((rpyc.Service.node.Max - rpyc.Service.node.node_id)/2, 0) + rpyc.Service.node.node_id
                n_id = 0
            top_DHT = {}
            bottom_DHT = {}
            # cut the DHT in half
            for key in rpyc.Service.node.DHT:
                if key > middle_id:
                    top_DHT[key] = rpyc.Service.node.DHT[key]
                else:
                    bottom_DHT[key] = rpyc.Service.node.DHT[key]
            #set the current nodes DHT as the bottom half
            rpyc.Service.node.DHT = bottom_DHT
            # save cur nodes' neighbour's ip
            n_ip = rpyc.Service.node.neighbour_ip
            # set cur nodes neighbour as new node
            rpyc.Service.node.neighbour_ip = node_ip
            # update cur node DHT with the bottom of DHT
            updateDHT(rpyc.Service.node.DHT)
            # debug message
            print str(rpyc.Service.node.node_id) + " " + str(rpyc.Service.node.neighbour_id) + " " + str(rpyc.Service.node.DHT) + " " + str(rpyc.Service.node.neighbour_ip) + " " + rpyc.Service.node.node_ip
            #return node_id, neighbour id, DHT, neighbour ip
            return middle_id, n_id, top_DHT, n_ip

    def exposed_get(self, key, ip):
        # returns the value that key stores
        print "got from" + ip
        # if the current nodes has the table that holds the key
        if rpyc.Service.node.node_id <= key < rpyc.Service.node.neighbour_id or rpyc.Service.node.neighbour_id < rpyc.Service.node.node_id < key:
            # print "get: " + str(key)
            # try:
            #     val = rpyc.Service.node.DHT[key]
            #     updateDHT(rpyc.Service.node.DHT)
            #     return val
            # except KeyError:
            #     return None
            # except ReferenceError:
            #     print "REFERENCE ERROR"
            #     return None
            with open("DHT.txt", "r") as f:
                for line in f:
                    file_key, file_value = line.partition(":")[::2]
                    if int(file_key.strip()) == key:
                        return int(file_value)
                f.close()
                return None
        else:
            #otherwise go to the next nodes hashtable and check it
            #change
            try:
                # rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
                print "get: " + str(key) + " not found" + " on server " + rpyc.Service.node.node_ip + " with ids: " + str(rpyc.Service.node.node_id) + " : " + str(rpyc.Service.node.neighbour_id)
                print "passed to: " + rpyc.Service.node.neighbour_ip
                return rpyc.Service.node.conn.root.get(key, rpyc.Service.node.node_ip)
            except socket.error:
                print "connection error"
                return None

    def exposed_put(self, key, value, ip):
        # puts a key : value pair into the correct HT
        print "got from " + ip
        print "doing put"
        # if the current table is the correct table add the key/value pair to the DHT
        if rpyc.Service.node.node_id <= key < rpyc.Service.node.neighbour_id or rpyc.Service.node.neighbour_id < rpyc.Service.node.node_id < key:
            # try:
            #     rpyc.Service.node.DHT[key] = value
            #     updateDHT(rpyc.Service.node.DHT)
            #     print str(key) + ":" + str(value) + " added to DHT at " + rpyc.Service.node.node_ip
            #     print rpyc.Service.node.DHT
            #     return True
            # except ReferenceError:
            #     print "Reference Error"
            #     return False
            with open("DHT.txt", "w") as f:
                f.write(str(key) + " : " + str(value))
                f.close()
            return True
        # look in the next table to add it to the DHT
        else:
            try:
                rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
                print "key: " + str(key) + " not found on server " + rpyc.Service.node.node_ip + " with ids: " + str(rpyc.Service.node.node_id) + " - " + str(rpyc.Service.node.neighbour_id)
                print "passed to: " + rpyc.Service.node.neighbour_ip
                return rpyc.Service.node.conn.root.put(key, value, rpyc.Service.node.node_ip)
                # return True
            except socket.error:
                print "connection error"
                return False


if __name__ == "__main__":
    #start the server on the current node
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18861)
    t.start()