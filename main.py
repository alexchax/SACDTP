from rpyc import *
import fileinput

def getValue(key, conn):
    return conn.root.get(key, "10.19.1.11")
def putValue(key, value, conn):
    return conn.root.put(key, value, "10.19.1.11")


def main():
    conn = connect("10.19.1.11", 18861)
    while True:
        line = raw_input()
        s = line.split(" ")
        if s[0] == "get":
            print getValue(int(s[1].strip()), conn)
        elif s[0] == "put":
            print putValue(int(s[1].strip()), int(s[2].strip()), conn)

if __name__ == "__main__":
    main()
