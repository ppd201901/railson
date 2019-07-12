import socket
import json

def client():
    host = socket.gethostname()
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))


    para = False
    while para==False:
        nome = input("Nome -> ")
        nivel = input("Nivel(A,B,C,D) -> ")
        salario = input("Salario (999999999.99) -> ")
        numDependentes = input("Num. Dependentes -> ")

        if(nome=="" and nivel=="" and salario=="" and numDependentes==""):
            break;

        obj={
            "func":"salarioLiquido",
            "nome":nome,
            "nivel":nivel.upper(),
            "salario":float(salario),
            "numDependentes":int(numDependentes)
        }
        msg = json.dumps(obj)
        client_socket.send(msg.encode())
        data = client_socket.recv(1024).decode()

        print("\n" + data)

    client_socket.close()


if __name__ == '__main__':
    client()