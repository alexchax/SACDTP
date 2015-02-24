# SACDTP
Implementing chord distributed hash table

Yay :)


If you haven't already, set up a repo for your project, and put a link to it under "OUR PROJECTS" in the CourseSpaces Forum! You will be demo-ing next week (Lab 6) based on what is there, and roughly it should contain:

a copy of your source code, and instructions on how we can compile / run your code
- 

a description of the following:

the structure of your code, including any major interfaces you implemented
for example, in the 2PC project, the RPC interface your replicas expose to the coordinator
- used RPyC to implement remote procedure calls.
- used GeeProject Nodes to implement "users".
- used fabric to install everything to servers

how you handle failures
for example, in the 2PC project, how are failures reflected to clients via the RPC interface that the coordinator exposes, if at all
- handle errors when trying to connect to another server that isnt responding

FAILURES THAT WE HAVE YET TO HANDLE
- balancing out the nodes evenly over the size of the hash table