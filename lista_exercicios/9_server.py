#lembrar de iniciar o name server
#C:\Users\rails\Google Drive\Faculdade\Materiais\mestrado\2 sem\sd\execicios\1\venv\Scripts>python.exe -m Pyro4.naming
import Pyro4

@Pyro4.expose

class Baralho(object):
    valor = 0
    naipe = ""

    def setValor(self,valor):
        self.valor=valor

    def setNaipe(self,naipe):
        self.naipe=naipe

    def getNomeCarta(self):
        msg=""
        if(self.valor>1 and self.valor<=10):
            msg = str(self.valor)+" de "
        else:
            if(self.valor==11):
                msg="Valete de "
            elif(self.valor==12):
                msg = "Dama de "
            elif(self.valor==13):
                msg = "Rei de "
            elif (self.valor == 1):
                msg = "Ás de "

        if(self.naipe==1):
            msg = msg+" ouros"
        elif(self.naipe==2):
            msg = msg + " paus"
        elif (self.naipe == 3):
            msg = msg + " copas"
        elif (self.naipe == 4):
            msg = msg + " espadas"

        return msg


daemon = Pyro4.Daemon()                # make a Pyro daemon
ns = Pyro4.locateNS()                  # find the name server
uri = daemon.register(Baralho)   # register the greeting maker as a Pyro object
ns.register("baralho.cartas", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                   # start the event loop of the server to wait for calls