# saved as greeting-client.py
import Pyro4

while(True):
    numCarta = input("Número da carta(1 a 13): ").strip()
    numNaipe = input("Número do naipe(1,2,3,4): ").strip()

    if(numCarta=="" and numNaipe==""):
        break

    numCarta=int(numCarta)
    numNaipe=int(numNaipe)

    if(numCarta<1 or numCarta>13):
        print("Numero da carta invalido")
    elif(numNaipe<1 or numNaipe>4):
        print("Número do naipe inválido")
    else:
        baralho = Pyro4.Proxy("PYRONAME:baralho.cartas")    # use name server object lookup uri shortcut
        baralho.setValor(numCarta)
        baralho.setNaipe(numNaipe)
        print(baralho.getNomeCarta())