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
    def __init__(self):
        self.neighbour_ip = None
        # arg(1) - ip of the node you want to connect to
        if len(sys.argv) == 2:
            self.neighbour_ip = sys.argv[1]
        self.DHT = getDHT()
        # maximum number of values in the DHT's
        self.Max = 1000000
        # node id - index of first value in current DHT
        self.node_id = 0
        # ip of the current node
        self.node_ip = socket.gethostbyname(socket.gethostname())
        # neighbour id - the id of the next node in the DHT
        self.neighbour_id = self.Max
        self.conn = None
        # port that the server is running on - always 18861
        self.neighbour_port = 18861
        print "connecting to: " + str(self.neighbour_ip)
        try:
            # try connecting to the server put in the args
            # setup connection using rpyc
            self.conn = rpyc.connect(self.neighbour_ip, self.neighbour_port)
            conn = self.conn
            # uses the inital connection method to split up the DHT
            self.node_id, self.neighbour_id, self.DHT, self.neighbour_ip = conn.root.connect(self.node_ip)
            # debug statement
            print str(self.node_id) + " " + str(self.neighbour_id) + " " + str(self.DHT) + " " + str(self.neighbour_ip) + " " + str(self.node_ip)
            updateDHT(self.DHT)
        except socket.error:
            # if arg not set or connection is unable to be set dont connect to the DHT
            self.conn = None
            print "connection not found"
        print self.conn
        super(MyService, self).__init__()

    # "exposed_-" allows other nodes to use a connection to call these functions
    def exposed_connect(self, node_ip):
        # connects a node to the Chord Scheme
        print "connected to: " + node_ip

        # if the current node is the only one in the Chord Scheme use this
        if self.node_id == 0 and self.neighbour_id == self.Max:
            print "there"
            middle_id = self.Max/2
            top_DHT = {}
            bottom_DHT = {}
            for key in self.DHT:
                if key > middle_id:
                    top_DHT[key] = self.DHT[key]
                else:
                    bottom_DHT[key] = self.DHT[key]
            self.DHT = bottom_DHT
            self.neighbour_id = middle_id
            updateDHT(bottom_DHT)
            self.neighbour_ip = node_ip
            print str(self.node_id) + " " + str(self.neighbour_id) + " " + str(self.DHT) + " " + str(self.neighbour_ip) + " " + str(self.node_ip)
            return middle_id, 0, top_DHT, node_ip
        else:
            n_id = 0
            # if current node is not the node connected to the "start" node
            if self.neighbour_id > self.node_id:
                print "here"
                middle_id = (self.neighbour_id - self.node_id)/2 + self.node_id
                n_id = self.neighbour_id
                self.neighbour_id = middle_id
            # if current node is the last in the chord
            else:
                print "here2"
                middle_id = round((self.Max - self.node_id)/2, 0) + self.node_id
                n_id = 0
            top_DHT = {}
            bottom_DHT = {}
            # cut the DHT in half
            for key in self.DHT:
                if key > middle_id:
                    top_DHT[key] = self.DHT[key]
                else:
                    bottom_DHT[key] = self.DHT[key]
            #set the current nodes DHT as the bottom half
            self.DHT = bottom_DHT
            # save cur nodes' neighbour's ip
            n_ip = self.neighbour_ip
            # set cur nodes neighbour as new node
            self.neighbour_ip = node_ip
            # update cur node DHT with the bottom of DHT
            updateDHT(self.DHT)
            # debug message
            print str(self.node_id) + " " + str(self.neighbour_id) + " " + str(self.DHT) + " " + str(self.neighbour_ip) + self.node_ip
            #return node_id, neighbour id, DHT, neighbour ip
            return middle_id, n_id, top_DHT, n_ip

    def exposed_get(self, key):
        # returns the value that key stores
        # if not rpyc.Service.conn:
            # try:
            #     #check to see if rpyc connection has been made
            #     rpyc.Service.conn = rpyc.connect(neighbour_ip, neighbour_port)
            # except socket.error:
            #     print "connection error"
            #     conn = None
            #     return None
        # if the current nodes has the table that holds the key
        if self.node_id <= key < self.neighbour_id or self.neighbour_id < self.node_id < key:
            print "get: " + str(key)
            try:
                return self.DHT[key]
            except KeyError:
                return None
        else:
            #otherwise go to the next nodes hastable and check it
            if self.conn:
                conn = self.conn
                print "get: " + str(key) + " not found" + " on server " + self.node_ip + " with ids: " + str(self.node_id) + " : " + str(self.neighbour_id)
                print "passed to: " + self.neighbour_ip
                return conn.root.get(key)

    def exposed_put(self, key, value):
        # puts a key : value pair into the correct HT
        # if not conn:
        #     try:
        #         # check if a connection is currently active
        #         conn = rpyc.connect(neighbour_ip, neighbour_port)
        #     except socket.error:
        #         conn = None
        #         return False
        # if the current table is the correct table add the key/value pair to the DHT
        if self.node_id <= key < self.neighbour_id or self.neighbour_id < self.node_id < key:
            self.DHT[int(key)] = int(value)
            updateDHT(self.DHT)
            print str(key) + ":" + str(value) + " added to DHT at " + self.node_ip
            return True
        # look in the next table to add it to the DHT
        else:
            print self.conn
            if self.conn:
                conn = self.conn
                print "key: " + str(key) + " not found on server " + self.node_ip + " with ids: " + str(self.node_id) + " - " + str(self.neighbour_id)
                print "passed to: " + self.neighbour_ip
                return conn.root.put(key, value)
            else:
                print "connection error"


if __name__ == "__main__":
    #start the server on the current node
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18861)
    t.start()