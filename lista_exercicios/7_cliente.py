import socket
import json

def client():
    host = socket.gethostname()
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))


    para = False
    while para==False:
        idade = input("Idade -> ")
        tempoServico = input("Tempo Servico -> ")

        if(idade=="" and tempoServico==""):
            break;

        obj={
            "func":"aposentadoria",
            "idade":int(idade),
            "tempoServico":int(tempoServico)
        }
        msg = json.dumps(obj)
        client_socket.send(msg.encode())
        data = client_socket.recv(1024).decode()

        print("\n" + data)

    client_socket.close()


if __name__ == '__main__':
    client()