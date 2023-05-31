import datetime
import json
import threading
from flask import Flask, jsonify, request
from flask_sse import sse
from datetime import datetime

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

class User:
    def __init__(self, name):
        self.name = name

class Leilao:
    def __init__(self, code, description, duration, value, winner):
        self.code = code
        self.description = description
        self.duration = duration
        self.value = value
        self.winner = winner
        self.subscribers = []

class Server(object):
    def __init__(self):
        self.clients = []
        self.leiloes = []

    def verifyEnd(self, code, duration):
        fim_leilao = datetime.strptime(duration, '%d/%m/%Y %H:%M:%S')
        leilao_filter = filter(lambda leilao: leilao.code == code, self.leiloes)
        leilao = list(leilao_filter)[0]
        while datetime.now() < fim_leilao:
            continue

        self.leiloes.remove(leilao)

        for sub in leilao.subscribers:
            sse.publish({"message": f"Fim do Leilao: {leilao.code}, Nome do vencedor: {leilao.winner}, Valor final: {leilao.value}"}, channel=sub)



    def createUser(self):
        name = request.form.get('name')
        newuser = User(name)
        self.clients.append(newuser)
        return ''

    def GetLeiloes(self):
        leiloes = []
        for leilao in self.leiloes:
            leiloes.append(leilao)

        json_string = json.dumps([ob.__dict__ for ob in leiloes])
        return jsonify(json_string)

    def createLeilao(self):
        user_name = request.form.get('user')
        code = request.form.get('code')
        description = request.form.get('description')
        price = request.form.get('price')
        duration = request.form.get('duration')
        winner = request.form.get('winner')
        newleilao = Leilao(code, description, duration, price, winner)
        fim_leilao = datetime.strptime(newleilao.duration, '%d/%m/%Y %H:%M:%S')
        if fim_leilao < datetime.now():
            sse.publish({"message": "Não é possível criar leilão com essa data"}, channel=user_name)
            return ''
        newleilao.subscribers.append(user_name)
        self.leiloes.append(newleilao)
        threading.Timer(1, self.verifyEnd, args=(newleilao.code, newleilao.duration)).start()
        for sub in self.clients:
            sse.publish({"message": "Novo leilão criado!"}, channel=sub.name)
        return ''


    def makeBid(self):
        code = request.form.get('code')
        value = request.form.get('value')
        user_name = request.form.get('user')
        leilao_filter = filter(lambda l: l.code == code, self.leiloes)
        leilao_list = list(leilao_filter)
        filter_user = filter(lambda user: user.name == user_name, self.clients)
        user = list(filter_user)[0].name
        if not leilao_list:
            sse.publish({"message": "Leilão não existe"}, channel=user)
            return None
        leilao = leilao_list[0]
        client_filter = filter(lambda sub: sub.name == user_name, self.clients)
        client = list(client_filter)[0]
        if int(leilao.value) < int(value):
            leilao.value = value
            leilao.winner = client.name
        elif int(leilao.value) > int(value):
            sse.publish({"message": "Valor menor do que o valor atual!"}, channel=user)
            return None
        if not user_name in leilao.subscribers:
            leilao.subscribers.append(user_name)
        for subscriber in leilao.subscribers:
            sse.publish({"message": f"Novo lance efetuado no leilão: {leilao.code}!"}, channel=subscriber)
        return ''

server = Server()

app.route('/createUser', methods=['POST'])(server.createUser)
app.route('/getLeiloes', methods=['GET'])(server.GetLeiloes)
app.route('/createLeilao', methods=['POST'])(server.createLeilao)
app.route('/makeBid', methods=['POST'])(server.makeBid)


if __name__ == '__main__':
    app.run()