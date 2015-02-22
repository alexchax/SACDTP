from rpyc import *

def getValue(key, conn):
    return conn.root.get(key)
def putValue(key, value, conn):
    return conn.root.put(key, value)


def main():
    conn = connect("localhost",18861)
    print putValue(15, 2, conn)
    print putValue(52, 1, conn)
    print putValue(52, 3, conn)
    print putValue(15, 2, conn)
    print getValue(15, conn)
    print getValue(52, conn)

if __name__ == "__main__":
    main()
