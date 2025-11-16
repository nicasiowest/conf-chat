import json
import uuid
from p2pnetwork.node import Node

class ChatNode(Node):
    def __init__(self, host, port, id=None):
        if id is None:
            id = f"node-{port}"

        super().__init__(host, port, id=id)

        # Username defaults to node-<port>, can change with /username
        self.username = id

        # Rooms this node is in
        self.rooms = set()

        # Track message IDs we've already processed (prevents loops)
        self.seen_messages = set()

        print(f"[STARTED] {self.username} listening on {host}:{port}")
        print("Type /help for commands.")

    # ----------------------------------------------------
    # Prevent library from printing dicts
    # ----------------------------------------------------
    def decode_data(self, data):
        try:
            return json.loads(data)
        except:
            return data

    # ----------------------------------------------------
    # P2P CALLBACKS
    # ----------------------------------------------------
    def inbound_node_connected(self, connected_node):
        print(f"[CONNECTED IN] {connected_node.id} connected to me.")

    def outbound_node_connected(self, connected_node):
        print(f"[CONNECTED OUT] I connected to {connected_node.id}")

    def node_disconnected(self, connected_node):
        print(f"[DISCONNECTED] {connected_node.id}")

    # ----------------------------------------------------
    # MAIN MESSAGE HANDLER + FORWARDING (GOSSIP MESH)
    # ----------------------------------------------------
    def node_message(self, connected_node, message):
        # message is either dict or plain string
        if not isinstance(message, dict):
            print(f"[{connected_node.id}] {message}")
            return

        # ---------------------------
        # 1. Deduplicate using ID
        # ---------------------------
        msg_id = message.get("id")
        if msg_id in self.seen_messages:
            return
        self.seen_messages.add(msg_id)

        # ---------------------------
        # 2. Forward (gossip) message
        # ---------------------------
        forward_raw = json.dumps(message)
        self.send_to_nodes(forward_raw)

        # ---------------------------
        # 3. Process message locally
        # ---------------------------
        mtype = message.get("type")
        sender = message.get("from")

        # Ignore our own messages
        if sender == self.username:
            return

        # ---- DIRECT MESSAGES ----
        if mtype == "direct":
            if message.get("to") == self.username:
                print(f"[DM][{sender} → you] {message.get('text')}")
            return

        # ---- ROOM MESSAGES ----
        if mtype == "room":
            room = message.get("room")
            if room in self.rooms:
                print(f"[ROOM:{room}][{sender}] {message.get('text')}")
            return

        # ---- PUBLIC ----
        if mtype == "chat":
            print(f"[PUBLIC][{sender}] {message.get('text')}")
            return

    # ----------------------------------------------------
    # HELPERS FOR SENDING MESSAGES (adds unique IDs)
    # ----------------------------------------------------
    def send_json(self, obj: dict):
        obj["id"] = str(uuid.uuid4())     # unique message ID
        raw = json.dumps(obj)
        self.send_to_nodes(raw)

    def send_public(self, text):
        msg = {
            "type": "chat",
            "from": self.username,
            "text": text,
        }
        self.send_json(msg)

    def send_direct(self, target_user, text):
        msg = {
            "type": "direct",
            "from": self.username,
            "to": target_user,
            "text": text,
        }
        self.send_json(msg)

    def send_room(self, room, text):
        if room not in self.rooms:
            print(f"You are not in room '{room}'. Use /join {room}.")
            return

        msg = {
            "type": "room",
            "from": self.username,
            "room": room,
            "text": text,
        }
        self.send_json(msg)


# ----------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------
def start_node(host, port, connect_to=None):
    node = ChatNode(host, port)
    node.start()

    # Optional bootstrap
    if connect_to:
        ip, p = connect_to.split(":")
        node.connect_with_node(ip, int(p))

    try:
        while True:
            line = input("> ").strip()
            if not line:
                continue

            if line.startswith("/"):
                parts = line.split()
                cmd = parts[0].lower()

                # Quit
                if cmd == "/quit":
                    break

                # Change username
                elif cmd == "/username" and len(parts) >= 2:
                    node.username = parts[1]
                    print(f"[INFO] Username set to {node.username}")

                # Direct message
                elif cmd == "/msg" and len(parts) >= 3:
                    target = parts[1]
                    text = " ".join(parts[2:])
                    node.send_direct(target, text)

                # Join room
                elif cmd == "/join" and len(parts) >= 2:
                    room = parts[1]
                    node.rooms.add(room)
                    print(f"[ROOM] Joined room '{room}'")

                # Leave room
                elif cmd == "/leave" and len(parts) >= 2:
                    room = parts[1]
                    if room in node.rooms:
                        node.rooms.remove(room)
                        print(f"[ROOM] Left room '{room}'")
                    else:
                        print(f"You are not in room '{room}'.")

                # List rooms
                elif cmd == "/rooms":
                    print("Rooms:", ", ".join(sorted(node.rooms)) or "(none)")

                # Send room message
                elif cmd == "/room" and len(parts) >= 3:
                    room = parts[1]
                    text = " ".join(parts[2:])
                    node.send_room(room, text)

                # Help
                elif cmd == "/help":
                    print("Commands:")
                    print("  /username <name>       - set your username")
                    print("  /msg <user> <text>     - send direct/private message")
                    print("  /join <room>           - join a conference room")
                    print("  /leave <room>          - leave a room")
                    print("  /rooms                 - list rooms joined")
                    print("  /room <room> <text>    - send message to a room")
                    print("  /quit                  - exit")

                else:
                    print("Unknown command. Use /help.")

            else:
                node.send_public(line)

    except KeyboardInterrupt:
        print("\n[CTRL+C] Shutting down...")

    finally:
        node.stop()
        print("[STOPPED] Node closed.")


# ----------------------------------------------------
# PROGRAM ENTRY
# ----------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        start_node(sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) == 4:
        start_node(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    else:
        print("Usage:")
        print("  py ConfChat-Minimal.py <host> <port>")
        print("  py ConfChat-Minimal.py <host> <port> <connect_ip:port>")
