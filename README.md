# SACDTP
Implementing chord distributed hash table

With this source code, and a slicelet gathered from gee-project.org, you can setup your own Distributed Hash Table Chord
implementation.
# Setting up your servers.
* Once you have a slicelet with it's fab file, (assuming you've already installed fab and know how to use it) simply copy the host names from your fab file and replace the host names in the fab file from this repo.
* Run 'fab setup_servers' to get all of the needed applications installed on all of the servers.
* Prepare an input.txt file (or use/change the one in the repo) so that the main.py file has instructions on which values to put under which ids.

# Running your servers.
* You'll need three terminal windows open to keep track of your output.
* FIRST, set up the connection your original server 'fab run_server' in the first terminal window. You'll see an ip for the first server, remember it.
* Edit the fab file section "run_servers" in the command where it says "run('python server.py ')" replace with the ip of the first server.
* Then, set up the connection from all other servers to the original server 'fab run_servers' in the second terminal window,
* Lastly, run the main function with your input to put in the values, and then get them respectively 'fab the_special'.

# Running without Slicelet
* First setup a server (python server.py)
* next, if connecting from another machine use:
  * python server.py <1st servers ip>
* if connecting from same machine or want to use a different port
  * python server.py <server ip(connecting to)> <server port (default 18861)> <local port>
a description of the following:
* the structure of your code
  * we have a Rpyc server which has 7 exposed methods
    * put, get, get_node, get_conn_info, connect, update_numbers, update_finger_table
  * put(key, value)
    * finds correct node then adds the key value pair to the hashtable
  * get(key)
    * finds the correct node then adds returns the value at that key (returns None if no key/value pair is found
  * get_node(get_from, att)
    * gets value from a numbered node (get_from is the number) that is equal to the attribute string
  * get_conn_info
    * returns a list of all connections in the DHT in the form ((<node ip>, <node port>, <node id>, <neighbour id>),...)
  * connect(node_ip, node_port)
    * connects this node to the node that this call is made on. This splits up the hashtable and re-evalutates all the other data that is changed.
  * update_numbers
    * recurisvly updates all the numbers(node numbers, max) of all nodes in the system.
  * update_finger_table
    * recurisvly updates all the finger tables of all nodes in the system.
    
major interfaces you implemented
* used RPyC to implement remote procedure calls.
* used GeeProject Nodes to implement "users".
* used fabric to install everything to servers

how you handle failures
* handle errors when trying to connect to another server that isn't responding.
* handled error of keys not being found
* had a coding failure involving weakly referenced objects (it was a dictionary) so we swapped over to text files
* handled errors when updating numbers and finger table
* Further Failures to handle
* Error when disconnection

# Test cases
In order to test that each of the servers worked, we put at least one value in each of the servers and watched as it traversed through the server output to find where to place the value and where to get the value from. At points we had trouble figuring out which server was connected to which other server, so we made test cases to see where the id's split so that we'd know which servers were unavailable.

#Implementation
What has been implemented
* Basic Distributed Hashtable with many of the major failures being detected
* Allowing for use on any network even on a single computer(still distributed as there are multiple programs running on each computer)
* Dynamically Allocated Size of hash table (when connected looks for the best nods to connect between)
What was tried to be implemented
* finger tables
  * finger tables could not be implemented because the way rpyc works is that it hangs until a command has been completed (hence remote procedure call) this came to a problem as the update_finger_table was a recursive call which updated them all at once. This became an issue when a node tried to get the information from the node that called the update_finger_table command as it was hanging so it wouldn’t return anything. This meant that you could not reach any nodes past it as well. We tried using Async callbacks and BgServiceThreads but none seemed to work.

What needs to be implemented and why it couldn’t be
* disconnection
  * with the current setup it was impossible to reconnect a client after a neighbour node disconnected as we could not get the finger tables working. with the finger tables it would be easily implemented.
