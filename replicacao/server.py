#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json
import sqlite3
import sys
import os
import _thread
import time

args = sys.argv
if(len(args)>1):
    nomeServer = args[1]
    portaServer = args[2]
else:
    nomeServer = 'srv0'
    portaServer = 8000

host = '0.0.0.0'
port = int(portaServer)

SERVIDORES = []

dbFile = 'db/'+nomeServer+'.db';

server_socket = socket.socket()
server_socket.bind((host, port))

server_socket.listen(2)

def getConnReplicas():
    global SERVIDORES
    data = SERVIDORES.copy() # 1 dia inteiro perdido por causa da falta de um .copy

    connRep = [];
    data.pop(0);##remove o central
    for servidor in data:
        try:
            cnn = client(servidor["host"],int(servidor["port"]))
            connRep.append(cnn)
        except:
            #erro de conexao com servidor de replica, descarta ele
            print("erro de conexao servidor de replica: "+json.dumps(servidor))
    return connRep;

def insereReplicas(obj):
    connrep = getConnReplicas();
    qtdSucesso = 0
    try:
        for conn in connrep:
            conn.send(json.dumps(obj).encode());
            data = conn.recv(1024).decode();
            ret= json.loads(data)
            if(ret["success"]):
                qtdSucesso = qtdSucesso+1
            else:
                raise Exception("Erro na transação da replica");


        for conn in connrep:
            conn.send(json.dumps({"func":"commit"}).encode());
            data = conn.recv(1024).decode();
            conn.close();

        return True
    except Exception as error:
        print(error)
        qtdRollback=0
        for conn in connrep:
            if(qtdRollback<qtdSucesso):
                conn.send(json.dumps({"func":"rollback"}).encode())
                data = conn.recv(1024).decode();
                conn.close();
    return False

def server(conn,address,lock):
    lock.acquire();
    bancoExiste = os.path.isfile(dbFile)
    if (bancoExiste == False):
        db = sqlite3.connect(dbFile)
        cursor = db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS leitura(id INTEGER PRIMARY KEY AUTOINCREMENT, ds_dispositivo TEXT, ds_leitura TEXT)")
    else:
        db = sqlite3.connect(dbFile)
        cursor = db.cursor()

    while True:
        print("Connection from: " + str(address))

        data = conn.recv(1024).decode()
        if not data:
            break
        obj = json.loads(data)

        if(obj["func"]=="insere"):
            cursor.execute('INSERT INTO leitura (ds_dispositivo,ds_leitura) VALUES (?,?)', (obj['data']['ds_dispositivo'], obj['data']['ds_leitura']))
            obj["func"] = "insereReplica"
            ret = insereReplicas(obj)
            if(ret):
                db.commit();
            else:
                db.rollback();
            conn.send(str(ret).encode())
        elif(obj["func"]=="insereReplica"):
            try:
                cursor.execute('INSERT INTO leitura (ds_dispositivo,ds_leitura) VALUES (?,?)', (obj['data']['ds_dispositivo'], obj['data']['ds_leitura']))
                conn.send(json.dumps({"func": "insereReplicaRetorno", "success": True}).encode())
            except Exception as error:
                conn.send(json.dumps({"func":"insereReplicaRetorno", "success": False, "message": str(error)}).encode())
        elif(obj["func"]=="commit"):
            try:
                db.commit()
                conn.send(json.dumps({"func": "commitRetorno", "success": True}).encode())
            except:
                conn.send(json.dumps({"func": "commitRetorno", "success": False}).encode())
        elif (obj["func"] == "rollback"):
            try:
                db.rollback()
                conn.send(json.dumps({"func": "commitRetorno", "success": True}).encode())
            except:
                conn.send(json.dumps({"func": "commitRetorno", "success": False}).encode())
        else:
            msg="Função não encontrada"
            conn.send(msg.encode())

    lock.release();
    db.close()
    conn.close()
    _thread.exit()

def client(host,port):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    return client_socket

def sinalDeVida(lock):
    global SERVIDORES
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(3)
    obj = {'func' : 'sinalDeVida','data' : {"host": host,"port":port}}
    while True:
        try:
            server.sendto(json.dumps(obj).encode(), ('<broadcast>', 8880))
            #print("Sinal de vida enviado!")
            data = server.recv(1024)
            print("Resposta Sinal de vida. %s"%data)
            lock.acquire()
            SERVIDORES = json.loads(data.decode())
            lock.release()

        except Exception as error:
            print(str(error))


        time.sleep(2)

lock = _thread.allocate_lock()
_thread.start_new_thread(sinalDeVida, tuple([lock]))
while True:
    print('Aguardando.....')
    con, cliente = server_socket.accept()
    _thread.start_new_thread(server, tuple([con, cliente, lock]))

server_socket.close()