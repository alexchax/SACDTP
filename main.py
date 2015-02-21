from rpyc import *
import sys,os

node_id = 0
neighbour_id = 10

def getValue(key, DHT):
    if node_id < key < neighbour_id:
        return DHT[key]
    else:
        conn = connect("localhost", 18861)
        return conn.root.get(key)



def updateDHT(DHT):
    open("DHT1.txt", "w").close()
    with open("DHT.txt", "w") as DHTFile:
        for key in DHT:
            print "adding " + str(key) + " : " + str(DHT[key]) + " to DHT"
            DHTFile.write(str(key) + " : " + str(DHT[key]) + "\n")


def putValue(key, value, DHT):
    if node_id < key < neighbour_id:
        DHT[key] = value
        updateDHT(DHT)
        return True
    else:
        conn = connect("localhost", 18861)
        return conn.root.put(key, value)


def getDHT():
    DHT = {}
    with open("DHT.txt", "r") as DHTFile:
        for line in DHTFile:
            print line.partition(":")
            key, value = line.partition(":")[::2]
            DHT[int(key.strip())] = int(value.strip())
    return DHT


def main():
    key = 15
    DHT = getDHT()
    print putValue(key, 2, DHT)
    print putValue(5, 1, DHT)
    print putValue(5, 3, DHT)
    print putValue(15, 2, DHT)
    print getValue(key, DHT)

if __name__ == "__main__":
    main()
