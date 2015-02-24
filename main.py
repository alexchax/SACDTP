from time import sleep
from rpyc import *
import sys

def getValue(key, conn):
    return conn.root.get(key, "localhost")
def putValue(key, value, conn):
    return conn.root.put(key, value, "localhost")


def main():
    conn = connect("localhost", 18861)
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            for line in f:
                s = line.split(" ")
                if s[0] == "get" and len(s) == 2:
                    print getValue(int(s[1].strip()), conn)
                if s[0] == "put" and len(s) == 3:
                    print putValue(int(s[1].strip()),int(s[2].strip()), conn)
                sleep(1)
    else:
        while True:
            line = raw_input()
            if line == "exit":
                exit()
            s = line.split(" ")
            if s[0] == "get" and len(s) == 2:
                print getValue(int(s[1].strip()), conn)
            elif s[0] == "put" and len(s) == 3:
                print putValue(int(s[1].strip()), int(s[2].strip()), conn)

if __name__ == "__main__":
    main()
