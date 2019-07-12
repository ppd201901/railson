import socket
import json
import time
import _thread

def client():
    host = '127.0.0.1'
    port = 8880

    client_socket = socket.socket()
    client_socket.connect((host, port))

    obj = {"func":"insere","data": {'ds_dispositivo': 'disp1', 'ds_leitura': 's1='+str(time.time())}}
    msg= json.dumps(obj)
    client_socket.send(msg.encode())
    data = client_socket.recv(1024).decode()
    print(data)
    client_socket.close()


if __name__ == '__main__':
    i=0
    while i< 5:
        _thread.start_new_thread(client, tuple([]))
        i= i+1

    while True:
        print(".")
        time.sleep(2)