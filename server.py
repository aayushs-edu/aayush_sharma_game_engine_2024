import socket
from _thread import *
import sys
import pickle


server = socket.gethostbyname(socket.gethostname())
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(4)
print(f"Waiting for a connection, Server Started at {server}")

# Player positions
# players = []
players = [(10, 10), (20, 20)]
currentPlayer = 0

# Networking methods
def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])

def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])

def threaded_client(conn : socket.socket, player):

    global currentPlayer
    
    conn.send(str.encode(make_pos(players[player]))) if players[player].__class__.__name__ == 'tuple' else conn.send(pickle.dumps(players[player]))

    reply = ""
    print(f'Client {player} connected.')
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = players[0]
                else:
                    reply = players[1]

                # print("Received: ", data)
                # print("Sending : ", reply)

            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    currentPlayer -= 1
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1