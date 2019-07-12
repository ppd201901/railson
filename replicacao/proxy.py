import socket
import json
import sqlite3
import sys
import os
import _thread
import time

args = sys.argv
#nomeServer = args[1]
#portaServer = args[2]

nomeServer = 'srvnomes'
portaServer = 8880

host = '0.0.0.0'
port = int(portaServer)


SERVIDORES = []

def serverNomes(lock):
    global SERVIDORES
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 8880))
    while True:
        data, addr = client.recvfrom(1024)
        #print("received message: %s" % data)
        obj = json.loads(data.decode())
        obj["data"]["host"]=addr[0]
        servidoresTemp = []
        lock.acquire()
        try:
            for i in range(len(SERVIDORES)):
                    srv = SERVIDORES[i]
                    #se encontrar o servidor atualiza o ts
                    if(obj["data"]['host']==srv["host"] and obj["data"]["port"]==srv["port"]):
                        raise Exception("Atualiza TS")

            #se passar por todos e nao encontrar adiciona a lista
            obj["data"]["ts"] = time.time()
            SERVIDORES.append(obj["data"])
        except Exception as error:
            #apena para parar o fluxo de execucao
            #print(error)
            SERVIDORES[i]["ts"] = time.time()
        finally:
            client.sendto(json.dumps(SERVIDORES).encode(),addr)

        lock.release()

    _thread.exit()

def detectaTimeOut(lock):
    global SERVIDORES
    while True:
        servidoresTemp=[]
        lock.acquire()
        for srv in SERVIDORES:
            if(srv["ts"]>=time.time()-3):
                servidoresTemp.append(srv);

        SERVIDORES = servidoresTemp
        print("Servidore ativos. %s" % json.dumps(SERVIDORES))
        lock.release()
        time.sleep(2)
    _thread.exit()

def client(host,port):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    return client_socket

def proxy(conn, address, lock):
    while True:

        data = conn.recv(1024)
        if not data:
            break

        obj=json.loads(data.decode())
        lock.acquire()
        try:
            if(len(SERVIDORES)>0):
                condest = SERVIDORES[0]
                print(condest["host"],condest["port"])
                cliente = client(condest["host"],condest["port"])
                cliente.send(data)
                data = cliente.recv(1024)
                conn.send(data)
                cliente.close()
                print("Conexão: " + str(address) + ' Enviada para -> ' + condest["host"] + ":" + str(condest["port"]))
            else:
                obj["success"] = False
                obj["func"] = obj["func"]+"Retorno"
                obj["message"] = "Nenhum servidor disponivel"
                conn.send(json.dumps(obj).encode())
        except Exception as error:
            print(str(error))

        lock.release()



    conn.close()


lock = _thread.allocate_lock()
_thread.start_new_thread(detectaTimeOut, tuple([lock]))
_thread.start_new_thread(serverNomes, tuple([lock]))
_thread.start_new_thread(proxy, tuple([lock]))

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(2)


while True:
    con, cliente = server_socket.accept()
    _thread.start_new_thread(proxy, tuple([con, cliente, lock]))