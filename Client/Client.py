import datetime
import string
import threading

class MessageReceiver(object):

    @Pyro5.api.expose
    @Pyro5.api.callback
    @Pyro5.api.oneway
    def newMessage(self, string):
        print(string)
def menu(client_uri):
    print("""
        1.Lista de leilões
        2.Adicionar leilão
        3.Fazer lance em um leilão
        """)
    ans = input("Escolha uma opção")
    if ans == "1":
        leiloes = server.GetLeiloes(client_uri);
        for leilao in leiloes:
            print(leilao)
        menu(client_uri)
    elif ans == "2":
         code = input("Digite o código do leilao")
         description = input("Digite a descrição do leilão")
         print("Digite o preço inicial do leilao")
         price = eval(input())
         year = int(input('Digite o ano do fim da duração: '))
         month = int(input('Digite o mes do fim da duração: '))
         day = int(input('Digite o dia do fim da duração: '))
         hours = int(input('Entre as horas do fim da duração: '))
         minutes = int(input('Entre os minutos do fim da duração: '))
         seconds = int(input('Entre os segundos do fim da duração: '))
         date = datetime.datetime(year, month, day, hours, minutes, seconds)
         date = date.strftime('%Y-%m-%d %H:%M:%S')
         server.createLeilao(client_uri, code, description, price, date, "Nínguem")
         menu(client_uri)
    elif ans == "3":
         print("Digite o código do leilao")
         code = input()
         print("Digite o preço inicial do leilao")
         value = input()
         server.makeBid(code, value, "", client_uri)
         menu(client_uri)

daemon = Pyro5.api.Daemon()
client_uri = daemon.register(MessageReceiver)
thread = threading.Thread(target=daemon.requestLoop)
thread.daemon = True
thread.start()
ns = Pyro5.core.locate_ns()
uri = ns.lookup("server")
server = Pyro5.api.Proxy(uri)
print("Digite o nome do usuario")
name = input()
createUser = server.createUser(name, "teste", client_uri)
menu(client_uri)

