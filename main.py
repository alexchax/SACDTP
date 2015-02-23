from rpyc import *
import fileinput

def getValue(key, conn):
    return conn.root.get(key)
def putValue(key, value, conn):
    return conn.root.put(key, value)


def main():
    conn = connect("10.19.1.11", 18861)
    while True:
        for line in fileinput.input():
            if
    print putValue(525, 2, conn)
    print getValue(525, conn)
    print putValue(50, 2, conn)
    print getValue(50, conn)
    print putValue(300, 4, conn)
    print getValue(300, conn)

if __name__ == "__main__":
    main()
