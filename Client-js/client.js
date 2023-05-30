const fetch = require('node-fetch');

async function listenToSSEEvents(userName) {
  const response = await fetch('http://localhost:5000/stream');
  const reader = response.body.getReader();

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      console.log('EventSource connection closed.');
      break;
    }

    const chunk = new TextDecoder('utf-8').decode(value);
    const event = parseSSEEvent(chunk);

    if (event.channel === userName) {
        console.log(event.data);
      }
  }
}

function parseSSEEvent(chunk) {
    const event = {};
    const lines = chunk.split('\n');
    for (const line of lines) {
      const colonIndex = line.indexOf(':');
      const field = line.slice(0, colonIndex).trim();
      const value = line.slice(colonIndex + 1).trim();
      if (field === 'event') {
        event.eventName = value;
      } else if (field === 'data') {
        event.data = value;
      } else if (field === 'id') {
        event.id = value;
      } else if (field === 'retry') {
        event.retry = parseInt(value, 10);
      } else if (field === 'channel') {
        event.channel = value;
      }
    }
    return event;
  }

async function createUser(username) {
  const url = 'http://localhost:5000/createUser';

  const parameters = new URLSearchParams();
  parameters.append('name', username);

  const response = await fetch(url, {
    method: 'POST',
    body: parameters
  });

  // Processar a resposta, se necessário
}

async function showMenu(userName) {
  console.log('Menu principal');
  console.log('1. Lista de leilões');
  console.log('2. Adicionar leilão');
  console.log('3. Fazer lance em um leilão');
  console.log('0. Sair');

  while (true) {
    console.log('Escolha uma opção: ');
    const option = await prompt();

    switch (option) {
      case '1':
        try {
          const url = 'http://localhost:5000/getLeiloes';
          const response = await fetch(url);
          const data = await response.json();

          console.log('Lista de leilões:');
          for (const leilao of data) {
            console.log(leilao);
          }
        } catch (error) {
          console.error('Erro ao obter a lista de leilões:', error);
        }
        break;
      case '2':
        console.log('Digite o código do leilão:');
        const leilaoCode = await prompt();
        console.log('Digite a descrição do leilão:');
        const leilaoDescription = await prompt();
        console.log('Digite o preço inicial do leilão:');
        const leilaoPrice = await prompt();
        console.log('Digite o ano do fim do leilão:');
        const leilaoYear = await prompt();
        console.log('Digite o mês do fim do leilão:');
        const leilaoMonth = await prompt();
        console.log('Digite o dia do fim do leilão:');
        const leilaoDay = await prompt();
        console.log('Digite as horas do fim do leilão:');
        const leilaoHour = await prompt();
        console.log('Digite os minutos do fim do leilão:');
        const leilaoMinutes = await prompt();
        console.log('Digite os segundos do fim do leilão:');
        const leilaoSeconds = await prompt();

        const url = 'http://localhost:5000/createLeilao';
        const endLeilao = new Date(
          leilaoYear,
          leilaoMonth - 1,
          leilaoDay,
          leilaoHour,
          leilaoMinutes,
          leilaoSeconds
        );

        const parameters = new URLSearchParams();
        parameters.append('user', userName);
        parameters.append('code', leilaoCode);
        parameters.append('description', leilaoDescription);
        parameters.append('price', leilaoPrice);
        parameters.append('duration', endLeilao.toISOString());
        parameters.append('winner', '');

        await fetch(url, {
          method: 'POST',
          body: parameters
        });

        console.log('Leilão criado com sucesso.');
        break;
      case '3':
        console.log('Opção 3 selecionada');
        // Lógica para a opção 3
        break;
      case '0':
        console.log('Saindo...');
        return;
      default:
        console.log('Opção inválida.');
        break;
    }
  }
}

function prompt() {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question('', (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function main() {
  console.log('Digite o nome do usuário:');
  const username = await prompt();

  await createUser(username);

  console.log('Ouvindo eventos SSE...');
  listenToSSEEvents();

  showMenu(username);
}

main().catch((error) => console.error('Erro:', error));
