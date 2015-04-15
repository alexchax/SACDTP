import os
import rpyc
import socket
import sys
# TODO set up finger table
# TODO find best possible connection rather than any connection
# TODO finger table - use to find connections if current connection breaks
# TODO use finger table to decrease time of look up

if len(sys.argv) >= 1:
    if sys.argv[1] == "--help":
        print "python server.py <neighbour ip> <neighbour port> <local port>"
        sys.exit()

def updateDHT(DHT):
    # writes the current DHT into a file (key) : (value)
    if not os.path.isdir(str(rpyc.Service.node.node_port)):
        os.makedirs(str(rpyc.Service.node.node_port))
    with open(str(rpyc.Service.node.node_port) + "/DHT.txt", "w") as DHTFile:
        for key in DHT:
            DHTFile.write(str(key) + " : " + str(DHT[key]) + "\n")
        DHTFile.close()



# class that stores all the information about the current node
# also stores all default variables (MAX and PORT currently)
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
        self.number = 0
        self.max = 1


# Service is the RPyC class we use that allows for RPC's
class MyService(rpyc.Service):
    rpyc.Service.node = Node()
    rpyc.Service.node.neighbour_ip = socket.gethostbyname(socket.gethostname())
    rpyc.Service.node.node_ip = socket.gethostbyname(socket.gethostname())
    print rpyc.Service.node.node_ip, rpyc.Service.node.neighbour_ip
    # pulls all values from a textfile and puts them into a DHT
    rpyc.Service.node.DHT = {}
    filename = str(rpyc.Service.node.node_port) + "/DHT.txt"
    try:
        with open(filename, "r") as DHTFile:
            for line in DHTFile:
                key, value = line.partition(":")[::2]
                rpyc.Service.node.DHT[int(key.strip())] = int(value.strip())
    except IOError:
        if not os.path.isdir(str(rpyc.Service.node.node_port)):
            os.makedirs(str(rpyc.Service.node.node_port))
        open(filename, 'w').close()
    print rpyc.Service.node.DHT
    # maximum number of values in the DHT's
    rpyc.Service.node.Max = 1000000
    rpyc.Service.node.pointer = rpyc.Service.node.DHT
    # node id - index of first value in current DHT
    rpyc.Service.node.node_id = 0
    # neighbour id - the id of the next node in the DHT
    rpyc.Service.node.neighbour_id = rpyc.Service.node.Max
    # arg(1) - ip of the node you want to connect to
    if len(sys.argv) >= 2 and not sys.argv[1] == "localhost":
        rpyc.Service.node.neighbour_ip = sys.argv[1]
    if len(sys.argv) >= 3:
        rpyc.Service.node.neighbour_port = sys.argv[2]
    if len(sys.argv) >= 4:
        rpyc.Service.node.node_port = sys.argv[3]
    try:
        # try connecting to the server put in the args
        # setup connection using rpyc
        rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
        print "getting conn info"
        conn_list = rpyc.Service.node.conn.root.get_connection_info(None, None)
        # find best insertion and update accordingly
        best_ip = conn_list[0][0]
        best_port = conn_list[0][1]
        if conn_list[0][3] == 0:
            largest_d = rpyc.Service.node.Max - conn_list[0][2]
        else:
            largest_d = conn_list[0][3] - conn_list[0][2]
        for l in conn_list:
            if l[3] - l[2] > largest_d:
                best_ip = l[0]
                best_port = l[1]
                if l[3] == 0:
                    largest_d = rpyc.Service.node.Max - l[2]
                else:
                    largest_d = l[3] - l[2]

        rpyc.Service.node.neighbour_ip = best_ip
        rpyc.Service.node.neighbour_port = best_port
        print best_ip, best_port, largest_d
        print "done getting conn info"
        # uses the inital connection method to split up the DHT
        rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
        rpyc.Service.node.node_id, rpyc.Service.node.neighbour_id, rpyc.Service.node.DHT, rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port, rpyc.Service.node.number, rpyc.Service.node.max = rpyc.Service.node.conn.root.connect(rpyc.Service.node.node_ip, rpyc.Service.node.node_port)
        updateDHT(rpyc.Service.node.DHT)
        print rpyc.Service.node.node_ip, ":", rpyc.Service.node.node_port, "-->", rpyc.Service.node.neighbour_ip, ":", rpyc.Service.node.neighbour_port
        print "(", rpyc.Service.node.node_id, ",", rpyc.Service.node.neighbour_id, ")"
        print "number is: " + str(rpyc.Service.node.number)
        print "max is: ", rpyc.Service.node.max
    except socket.error:
        # if arg not set or connection is unable to be set dont connect to the DHT
        print "connection not found"
    try:
        print "updating numbers"
        print rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port
        rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
        print "sending", rpyc.Service.node.number
        rpyc.Service.node.conn.root.update_numbers(rpyc.Service.node.node_ip, rpyc.Service.node.node_port, rpyc.Service.node.number, rpyc.Service.node.max)
        print "done updating numbers"
    except socket.error:
        print "error updating numbers"
    try:
        print "updating finger table"
        rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
        rpyc.Service.node.conn.root.update_finger_table(rpyc.Service.node.node_ip, rpyc.Service.node.node_port, rpyc.Service.node.number)
        print "done updating finger table"
    except socket.error:
        print "error updating finger table"
    print "ready..."
    print "numbers:", rpyc.Service.node.number, rpyc.Service.node.max
    print "(", rpyc.Service.node.node_id, ",", rpyc.Service.node.neighbour_id, ")"

    def exposed_get_connection_info(self, exit_ip, exit_port):
        l = ()
        if not exit_ip:
            exit_ip = rpyc.Service.node.node_ip
            exit_port = rpyc.Service.node.node_port
        if rpyc.Service.node.neighbour_ip == exit_ip and rpyc.Service.node.neighbour_port == exit_port:
            return l + ((rpyc.Service.node.node_ip, rpyc.Service.node.node_port, rpyc.Service.node.node_id, rpyc.Service.node.neighbour_id),)
        try:
            if not rpyc.Service.node.conn:
                rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
            return l + ((rpyc.Service.node.node_ip, rpyc.Service.node.node_port, rpyc.Service.node.node_id, rpyc.Service.node.neighbour_id),) + (rpyc.Service.node.conn.root.get_connection_info(exit_ip, exit_port))
        except socket.error:
            return "Unable to connect"

        # list of pairs (ip, port, node_id, neighbour_id)

    # "exposed_-" allows other nodes to use a connection to call these functions
    def exposed_connect(self, node_ip, node_port):
        # connects a node to the Chord Scheme
        print "connected to: " + str(node_ip) + " : " + str(node_port)

        # if the current node is the only one in the Chord Scheme use this
        if rpyc.Service.node.node_id == 0 and rpyc.Service.node.neighbour_id == rpyc.Service.node.Max:
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
            rpyc.Service.node.neighbour_port = node_port
            rpyc.Service.node.max += 1
            #node_id, #neighbour_id, neighbour_ip
            print rpyc.Service.node.node_ip, ":", rpyc.Service.node.node_port, "-->",rpyc.Service.node.neighbour_ip, ":", rpyc.Service.node.neighbour_port
            print "(", rpyc.Service.node.node_id, ",", rpyc.Service.node.neighbour_id, ")"
            return middle_id, 0, top_DHT, rpyc.Service.node.node_ip, rpyc.Service.node.node_port, rpyc.Service.node.number+1, rpyc.Service.node.max
        else:
            # if current node is not the node connected to the "start" node
            if rpyc.Service.node.neighbour_id > rpyc.Service.node.node_id:
                middle_id = (rpyc.Service.node.neighbour_id - rpyc.Service.node.node_id)/2 + rpyc.Service.node.node_id
                n_id = rpyc.Service.node.neighbour_id
                rpyc.Service.node.neighbour_id = middle_id
            # if current node is the last in the chord
            else:
                middle_id = round((rpyc.Service.node.Max - rpyc.Service.node.node_id)/2, 0) + rpyc.Service.node.node_id
                n_id = 0
            top_DHT = {}
            n_ip = rpyc.Service.node.neighbour_ip
            n_port = rpyc.Service.node.neighbour_port
            # set cur nodes neighbour as new node
            rpyc.Service.node.neighbour_ip = node_ip
            rpyc.Service.node.neighbour_port = node_port
            rpyc.Service.node.neighbour_id = middle_id
            rpyc.Service.node.max += 1
            # update cur node DHT with the bottom of DHT
            # debug message
            print rpyc.Service.node.node_ip, ":", rpyc.Service.node.node_port, "-->",rpyc.Service.node.neighbour_ip, ":", rpyc.Service.node.neighbour_port
            print "last connection", "(", rpyc.Service.node.node_id, ",", rpyc.Service.node.neighbour_id, ")"
            #return node_id, neighbour id, DHT, neighbour ip, neighbour port
            return middle_id, n_id, top_DHT, n_ip , n_port, rpyc.Service.node.number+1, rpyc.Service.node.max

    def exposed_get(self, key):
        # returns the value that key stores
        # if the current nodes has the table that holds the key
        if rpyc.Service.node.node_id <= key < rpyc.Service.node.neighbour_id or rpyc.Service.node.neighbour_id < rpyc.Service.node.node_id < key:
            with open(str(rpyc.Service.node.node_port) + "/DHT.txt", "r") as f:
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
                return rpyc.Service.node.conn.root.get(key)
            except socket.error:
                print "connection error"
                return None

    def exposed_update_numbers(self, exit_ip, exit_port, number, m):
        print "updating numbers"
        print "max is", m
        print "number is", (number + 1) % m
        if not (rpyc.Service.node.node_ip == exit_ip and rpyc.Service.node.node_port == exit_port):
            rpyc.Service.node.number = (number + 1) % m
            rpyc.Service.node.max = m
            try:
                rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
            except socket.error:
                print "connection error while updating numbers"
                print "numbers:", rpyc.Service.node.number, m
                return
            if not (rpyc.Service.node.neighbour_ip == exit_ip and rpyc.Service.node.neighbour_port == exit_port):
                print "sending...."
                print "number sent:", (number+1)%m
                print rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port
                rpyc.Service.node.conn.root.update_numbers(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port, rpyc.Service.node.number, m)
                print "done..."
        print "numbers:", rpyc.Service.node.number, m
        print "done updating numbers"

    def exposed_update_finger_table(self, exit_ip, exit_port, exit_number):
        print "updating finger table"
        try:
            cur_num = rpyc.Service.node.number
            index = 1
            max = rpyc.Service.node.max
            with open(str(rpyc.Service.node.node_port) + "/FingerTable.txt", "w") as f:
                pass
            get_from = cur_num
            with open(str(rpyc.Service.node.node_port) + "/FingerTable.txt", "a") as f:
                while index < max:
                    print "finger table"
                    # print index, max
                    get_from = (cur_num+(2**(index-1))) % 2**max % max
                    if not cur_num == get_from:
                        # print rpyc.Service.node.node_ip, exit_ip
                        # print rpyc.Service.node.node_port, exit_port
                        # print get_from
                        if not rpyc.Service.node.conn:
                            rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
                        if not (rpyc.Service.node.neighbour_port == exit_port and rpyc.Service.node.neighbour_ip == exit_ip):
                            ip = rpyc.Service.node.conn.root.get_node(get_from, "node_ip", exit_number)
                            port = rpyc.Service.node.conn.root.get_node(get_from, "node_port", exit_number)
                            id1 = rpyc.Service.node.conn.root.get_node(get_from, "node_id", exit_number)
                            id2 = rpyc.Service.node.conn.root.get_node(get_from, "neighbour_id", exit_number)
                            if not ip == -1:
                                f.write(str(ip) + "|" + str(port) + "|" + str(id1) + "|" + str(id2) + "\n")
                            # print rpyc.Service.node.conn.root.get_node(get_from, "node_ip", exit_number), rpyc.Service.node.conn.root.get_node(get_from, "node_id", exit_number), rpyc.Service.node.conn.root.get_node(get_from, "neighbour_ip", exit_number)
                    index += 1
                if not (rpyc.Service.node.neighbour_ip == exit_ip and rpyc.Service.node.neighbour_port == exit_port):
                    if not rpyc.Service.node.conn:
                        rpyc.Service.node.conn == rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
                    rpyc.Service.node.conn.root.update_finger_table(exit_ip, exit_port, exit_number)
                print "done index"
        except socket.error:
            print "error updating finger table"
        print "done updating finger table"

    def exposed_get_node(self, get_from, att, exit_number):
        # print "getting from", get_from, rpyc.Service.node.number
        if get_from == rpyc.Service.node.number:
            print "returning value"
            if att == "node_ip":
                return rpyc.Service.node.node_ip
            elif att == "node_port":
                return rpyc.Service.node.node_port
            elif att == "node_id":
                return rpyc.Service.node.node_id
            elif att == "number":
                return rpyc.Service.node.number
            elif att == "neighbour_ip":
                return rpyc.Service.node.neighbour_ip
            elif att == "neighbour_id":
                return rpyc.Service.node.neighbour_id
        else:
            if(rpyc.Service.node.number + 1 % rpyc.Service.node.max) == exit_number:
                return -1
            return rpyc.Service.node.conn.root.get_node(get_from, att, exit_number)

    def exposed_put(self, key, value):
        # puts a key : value pair into the correct HT
        print "doing put"
        # if the current table is the correct table add the key/value pair to the DHT
        if rpyc.Service.node.node_id <= key < rpyc.Service.node.neighbour_id or rpyc.Service.node.neighbour_id < rpyc.Service.node.node_id < key:
            with open(str(rpyc.Service.node.node_port) + "/DHT.txt", "a") as f:
                f.write(str(key) + " : " + str(value)+"\n")
                f.close()
            return True
        # look in the next table to add it to the DHT
        else:
            try:
                rpyc.Service.node.conn = rpyc.connect(rpyc.Service.node.neighbour_ip, rpyc.Service.node.neighbour_port)
                print "key: " + str(key) + " not found on server " + rpyc.Service.node.node_ip + ":" + str(rpyc.Service.node.node_port) + " with ids: " + str(rpyc.Service.node.node_id) + " - " + str(rpyc.Service.node.neighbour_id)
                print "passed to: " + rpyc.Service.node.neighbour_ip + ":" + str(rpyc.Service.node.neighbour_port)
                return rpyc.Service.node.conn.root.put(key, value)
                # return True
            except socket.error:
                print "connection error"
                return False

if __name__ == "__main__":
    #start the server on the current node
    from rpyc.utils.server import ThreadedServer
    p = 18861

    if len(sys.argv) == 4:
        p = int(sys.argv[3])
    t = ThreadedServer(MyService, port=p)
    t.start()
