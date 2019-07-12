import socket
import json
import msgpack
import time
from multiprocessing import Process
import random
import string

def client():
    host = socket.gethostname()
    port = 5000




    para = False
    while para==False:
        para= True
        client_socket = socket.socket()
        client_socket.connect((host, port))
        print(client_socket.recv(1024))
        nome = ''.join([random.choice(string.ascii_letters) for n in range(8)])
        nivel = ''.join([random.choice('ABCD') for n in range(1)])
        salario = random.randint(1000,10000)
        numDependentes = random.randint(0,3)

        if(nome=="" and nivel=="" and salario=="" and numDependentes==""):
            break;

        obj={
            "func":"salarioLiquido",
            "nome":nome,
            "nivel":nivel.upper(),
            "salario":float(salario),
            "numDependentes":int(numDependentes)
        }

        msg = msgpack.packb(obj, use_bin_type=True)
        #msg = json.dumps(obj)
        i=0
        while i<5:
            i=i+1
            client_socket.send(msg)
            data = client_socket.recv(1024).decode()
            if data!="\nErro":
                break
            else:
                print("Erro Retry:"+str(i));
                time.sleep(1);

        #print("\n" + data)
        client_socket.close()



if __name__ == '__main__':
    i=0
    while i<200:
        i=i+1
        p = Process(target=client)
        p.start()
