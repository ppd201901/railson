import socket
import json
import msgpack
import postgresql

class Conexao(object):
    _db=None
    def __init__(self, banco):
        self._db = postgresql.open(banco)
    def manipular(self, sql):
        try:
            self._db.execute(sql)
        except:
            return False
        return True
    def consultar(self, sql):
        rs=None
        try:
            rs=self._db.prepare(sql)
        except:
            return None
        return rs

    def proximaPK(self, tabela, chave):
        sql='select max('+chave+') from '+tabela
        rs = self.consultar(sql)
        pk = rs.first()
        return pk+1
    def fechar(self):
        self._db.close()

host = socket.gethostname()
port = 5000

server_socket = socket.socket()
server_socket.bind((host, port))

server_socket.listen(2)
conn, address = server_socket.accept()

def server():

    print("Connection from: " + str(address))
    while True:
        data = conn.recv(1024)
        obj = msgpack.unpackb(data,raw=False)

        print(data)

        if not data:
            break
        #obj = json.loads(str(data))



        con = Conexao("pq://postgres:root@localhost/sd1")
        sql = "insert into leitura (ds_leitura,in_processado,dt_leitura,id_dispositivo) values ('" + json.dumps(obj) + "',false,now(),1)"
        if con.manipular(sql):
            print('inserido com sucesso!')
            msg = "Inserido"
        else:
            msg="erro ao inserir"
        print(con.proximaPK('leitura', 'id_leitura'))
#        rs = con.consultar("select * from leitura")
#        for linha in rs:
#            print(linha)
        con.fechar()

        conn.send(msg.encode())


    conn.close()


if __name__ == '__main__':
    server()