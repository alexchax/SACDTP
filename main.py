from rpyc import *
import sys,os


def getValue(key, DHT):
    return DHT[key]


def updateDHT(DHT):
    with open("DHT.txt", "w") as DHTFile:
        for key in DHT:
            DHTFile.write(key + " : " + str(DHT[key]))


def putValue(key, value, DHT):
    DHT[key] = value
    updateDHT(DHT)

def main():
    conn = classic.connect("localhost")
    key = "3"
    DHT = {}
    DHT = getDHT()
    putValue(key, 2, DHT)
    print getValue(key, DHT)


def getDHT():
    DHT = {}
    with open("DHT.txt", "r") as DHTFile:
        for line in DHTFile:
            key, value = line.partition(":")[::2]
            DHT[key.strip()] = value
    return DHT


if __name__ == "__main__":
    main()
