import rpyc
import socket
import sys

print sys.argv


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


class MyService(rpyc.Service):
    rpyc.Service.neighbour_ip = None
    # arg(1) - ip of the node you want to connect to
    if len(sys.argv) == 2:
        rpyc.Service.neighbour_ip = sys.argv[1]
    rpyc.Service.DHT = getDHT()
    # maximum number of values in the DHT's
    rpyc.Service.Max = 1000000
    # node id - index of first value in current DHT
    rpyc.Service.node_id = 0
    # ip of the current node
    rpyc.Service.node_ip = socket.gethostbyname(socket.gethostname())
    # neighbour id - the id of the next node in the DHT
    rpyc.Service.neighbour_id = rpyc.Service.Max
    rpyc.Service.conn = None
    # port that the server is running on - always 18861
    rpyc.Service.neighbour_port = 18861
    print "connecting to: " + str(rpyc.Service.neighbour_ip)
    try:
        # try connecting to the server put in the args
        # setup connection using rpyc
        rpyc.Service.conn = rpyc.connect(rpyc.Service.neighbour_ip, rpyc.Service.neighbour_port)
        conn = rpyc.Service.conn
        # uses the inital connection method to split up the DHT
        rpyc.Service.node_id, rpyc.Service.neighbour_id, rpyc.Service.DHT, rpyc.Service.neighbour_ip = conn.root.connect(rpyc.Service.node_ip)
        # debug statement
        print str(rpyc.Service.node_id) + " " + str(rpyc.Service.neighbour_id) + " " + str(rpyc.Service.DHT) + " " + str(rpyc.Service.neighbour_ip) + " " + str(rpyc.Service.node_ip)
        updateDHT(rpyc.Service.DHT)
    except socket.error:
        # if arg not set or connection is unable to be set dont connect to the DHT
        rpyc.Service.conn = None
        print "connection not found"
    print rpyc.Service.conn

    # "exposed_-" allows other nodes to use a connection to call these functions
    def exposed_connect(self, node_ip):
        # connects a node to the Chord Scheme
        print "connected to: " + node_ip

        # if the current node is the only one in the Chord Scheme use this
        if rpyc.Service.node_id == 0 and rpyc.Service.neighbour_id == rpyc.Service.Max:
            print "there"
            middle_id = rpyc.Service.Max/2
            top_DHT = {}
            bottom_DHT = {}
            for key in rpyc.Service.DHT:
                if key > middle_id:
                    top_DHT[key] = rpyc.Service.DHT[key]
                else:
                    bottom_DHT[key] = rpyc.Service.DHT[key]
            rpyc.Service.DHT = bottom_DHT
            rpyc.Service.neighbour_id = middle_id
            updateDHT(bottom_DHT)
            rpyc.Service.neighbour_ip = node_ip
            print str(rpyc.Service.node_id) + " " + str(rpyc.Service.neighbour_id) + " " + str(rpyc.Service.DHT) + " " + str(rpyc.Service.neighbour_ip) + " " + str(rpyc.Service.node_ip)
            return middle_id, 0, top_DHT, rpyc.Service.node_ip
        else:
            n_id = 0
            # if current node is not the node connected to the "start" node
            if rpyc.Service.neighbour_id > rpyc.Service.node_id:
                print "here"
                middle_id = (rpyc.Service.neighbour_id - rpyc.Service.node_id)/2 + rpyc.Service.node_id
                n_id = rpyc.Service.neighbour_id
                rpyc.Service.neighbour_id = middle_id
            # if current node is the last in the chord
            else:
                print "here2"
                middle_id = round((rpyc.Service.Max - rpyc.Service.node_id)/2, 0) + rpyc.Service.node_id
                n_id = 0
            top_DHT = {}
            bottom_DHT = {}
            # cut the DHT in half
            for key in rpyc.Service.DHT:
                if key > middle_id:
                    top_DHT[key] = rpyc.Service.DHT[key]
                else:
                    bottom_DHT[key] = rpyc.Service.DHT[key]
            #set the current nodes DHT as the bottom half
            rpyc.Service.DHT = bottom_DHT
            # save cur nodes' neighbour's ip
            n_ip = rpyc.Service.neighbour_ip
            # set cur nodes neighbour as new node
            rpyc.Service.neighbour_ip = node_ip
            # update cur node DHT with the bottom of DHT
            updateDHT(rpyc.Service.DHT)
            # debug message
            print str(rpyc.Service.node_id) + " " + str(rpyc.Service.neighbour_id) + " " + str(rpyc.Service.DHT) + " " + str(rpyc.Service.neighbour_ip) + rpyc.Service.node_ip
            #return node_id, neighbour id, DHT, neighbour ip
            return middle_id, n_id, top_DHT, n_ip

    def exposed_get(self, key):
        # returns the value that key stores
        # if not rpyc.Service.conn:
            # try:
            #     #check to see if rpyc connection has been made
            #     rpyc.Service.conn = rpyc.connect(rpyc.Service.neighbour_ip, rpyc.Service.neighbour_port)
            # except socket.error:
            #     print "connection error"
            #     rpyc.Service.conn = None
            #     return None
        # if the current nodes has the table that holds the key
        if rpyc.Service.node_id <= key < rpyc.Service.neighbour_id or rpyc.Service.neighbour_id < rpyc.Service.node_id < key:
            print "get: " + str(key)
            try:
                return rpyc.Service.DHT[key]
            except KeyError:
                return None
        else:
            #otherwise go to the next nodes hastable and check it
            if rpyc.Service.conn:
                conn = rpyc.Service.conn
                print "get: " + str(key) + " not found" + " on server " + rpyc.Service.node_ip + " with ids: " + str(rpyc.Service.node_id) + " : " + str(rpyc.Service.neighbour_id)
                print "passed to: " + rpyc.Service.neighbour_ip
                return conn.root.get(key)

    def exposed_put(self, key, value):
        # puts a key : value pair into the correct HT
        # if not rpyc.Service.conn:
        #     try:
        #         # check if a connection is currently active
        #         rpyc.Service.conn = rpyc.connect(rpyc.Service.neighbour_ip, rpyc.Service.neighbour_port)
        #     except socket.error:
        #         rpyc.Service.conn = None
        #         return False
        # if the current table is the correct table add the key/value pair to the DHT
        if rpyc.Service.node_id <= key < rpyc.Service.neighbour_id or rpyc.Service.neighbour_id < rpyc.Service.node_id < key:
            rpyc.Service.DHT[int(key)] = int(value)
            updateDHT(rpyc.Service.DHT)
            print str(key) + ":" + str(value) + " added to DHT at " + rpyc.Service.node_ip
            return True
        # look in the next table to add it to the DHT
        else:
            if rpyc.Service.conn:
                conn = rpyc.Service.conn
                print "key: " + str(key) + " not found on server " + rpyc.Service.node_ip + " with ids: " + str(rpyc.Service.node_id) + " - " + str(rpyc.Service.neighbour_id)
                print "passed to: " + rpyc.Service.neighbour_ip
                return conn.root.put(key, value)
            else:
                "connection error"


if __name__ == "__main__":
    #start the server on the current node
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18861)
    t.start()