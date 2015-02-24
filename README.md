# SACDTP
Implementing chord distributed hash table

Yay :)

With this source code, and a slicelet gathered from gee-project.org, you can setup your own Distributed Hash Table Chord implementation.

Setting up your servers.
-

- Once you have a slicelet with it's fab file, (assuming you've already installed fab and know how to use it) simply copy the host names from your fab file and replace the host names in the fab file from this repo.
- Run 'fab setup_servers' to get all of the needed applications installed on all of the servers.
- Prepare an input.txt file (or use/change the one in the repo) so that the main.py file has instructions on which values to put under which ids.

Running your servers.
-

You'll need three terminal windows open to keep track of your output.
- FIRST, set up the connection your original server 'fab run_server' in the first terminal window.
- Then, set up the connection from all other servers to the original server 'fab run_servers' in the second terminal window,
- Lastly, run the main function with your input to put in the values, and then get them respectively 'fab the_special'.


a description of the following:

the structure of your code
- for structure of code look at comments in code!

major interfaces you implemented
- used RPyC to implement remote procedure calls.
- used GeeProject Nodes to implement "users".
- used fabric to install everything to servers


how you handle failures
- handle errors when trying to connect to another server that isn't responding.
- handled error of keys not being found
- had a coding failure involving weakly referenced objects (it was a dictionary) so we swapped over to text files 

Test cases
-
In order to test that each of the servers worked, we put at least one value in each of the servers and watched as it traversed through the server output to find where to place the value and where to get the value from. 
At points we had trouble figuring out which server was connected to which other server, so we made test cases to see where the id's split so that we'd know which servers were unavailable. 

FAILURES THAT WE HAVE YET TO HANDLE
- balancing out the nodes evenly over the size of the hash table
