# conf-chat
A P2P Chat

Developed by: Nicasio Westlund

This is a peer to peer messaging system that uses python and p2pnetwork library
to make connections with other nodes. Once you have connected the nodes, you can
set your username, chat with other users, join chat rooms and send messages to 
these chat rooms, list the chat rooms you have joined, and leave the chat rooms.

To run this program:

Ensure that you have Python installed. https://www.python.org/downloads/

Ensure that you have p2pnetwork library installed. https://pypi.org/project/p2pnetwork/

Download the files from this GitHub repository. You should see the conf_chat.py
python file.

In a terminal session, navigate to the folder where the conf_chat.py file is
located.

Run: python conf_chat.py <ip_address> <port_number>
Example: python conf_chat.py 127.0.0.1 8001

You should see that you are initialized and listening on your port. This will 
set up the bootstrap node you need to connect with the other nodes.

Open another terminal session and start a new connection. Make sure you are
using a different port number.

Run: python conf_chat.py <ip_address> <port_number> <boostrap_ip_address:bootstrap_port_number>
Example: python conf_chat.py 127.0.0.1 8002 127.0.0.1:8001

This will connect to the bootstrap node you originally set up.

Repeat this as many times as you need, making sure the new nodes you set up are 
using a different port number from each other.

While running you are able to see a variety of commands. 

Type /help to see the list of commands.


The commands are as followed:

/username <name>        - set your username

/msg <user> <text>      - send direct/private message

/join <room>            - join a conference/chat room

/leave <room>           - leave a conference room

/rooms                  - list the rooms you have joined

/room <room> <text>     - send a message to the specified room

/quit                   - exit


Please try out these different commands and test out setting a username,
messaging other users, joining rooms, and messaging those rooms.

Once you are finished, you can exit with /quit.

I hope you enjoyed using this peer to peer messaging program.
