<div align="center">
  <h1>Avaliação de desempenho</h1>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10-6B5B95?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/React-18-8A2BE2?style=for-the-badge&logo=react&logoColor=white" alt="React" />
    <img src="https://img.shields.io/badge/PostgreSQL-15-9370DB?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Docker-D8BFD8?style=for-the-badge&logo=docker&logoColor=black" alt="Docker" />
  </p>
</div>

Plataforma web processa notas de funcionários através de uma estrutura hierárquica. O sistema cruza os dados do perfil ativo com o organograma de cargos. A restrição de negócio proíbe o envio de múltiplos formulários para a mesma pessoa na mesma semana.

## Arquitetura e fluxo de dados

O projeto divide os serviços em três contêineres independentes conectados pela mesma rede virtual.

* Interface: O front-end em React identifica o líder ativo através do armazenamento local. A tela exibe o histórico lido do banco de dados.
* Servidor: A API em Python recebe as notas numéricas. O código multiplica os valores brutos pelos pesos para calcular a média. As consultas SQL verificam a subordinação direta e indireta.
* Banco de dados: O PostgreSQL guarda as tabelas. O sistema armazena o registro imutável das avaliações neste ambiente.

## Preparação do ambiente

O código roda inteiramente dentro da ferramenta Docker. Você não precisa instalar linguagens de programação no seu computador.

1. Acesse o site oficial docker.com.
2. Baixe o instalador do Docker Desktop.
3. Execute o arquivo baixado no seu sistema.
4. Abra o programa Docker Desktop.
5. Deixe a aplicação ligada em segundo plano.

## Download do repositório

Obtenha os arquivos de texto para a sua máquina local.

1. Acesse a página do projeto no GitHub.
2. Pressione o botão verde escrito Code.
3. Escolha a opção Download ZIP.
4. Extraia a pasta compactada no seu computador.
5. Abra o terminal do seu sistema operacional.
6. Digite cd seguido de espaço e o caminho da pasta extraída.
7. Pressione a tecla enter.

## Inicialização do sistema

Os comandos a seguir constroem o banco de dados e ativam as rotas.

1. Digite docker-compose up --build no terminal.
2. Pressione a tecla enter.
3. Aguarde a finalização do processo.
4. Abra o seu navegador web.
5. Acesse o endereço http://localhost:3000 para utilizar a interface gráfica.
6. Pressione as teclas ctrl e c no terminal para encerrar a execução.

## Execução dos testes automatizados

Os testes de código verificam as regras matemáticas e as restrições de tempo.

1. Mantenha o sistema ligado no primeiro terminal.
2. Abra uma nova janela de terminal limpa.
3. Navegue até a pasta do projeto com o comando cd.
4. Digite docker-compose exec backend python -m unittest discover -s tests.
5. Pressione a tecla enter para ler o relatório.

## Documentação dos endpoints

A API fornece quatro pontos de acesso diretos ao banco de dados.

* GET /api/employees lista os trabalhadores em formato JSON.
* GET /api/subordinates/<leader_id> recebe o código do líder e devolve seus subordinados.
* GET /api/evaluations/<evaluated_id> informa as notas passadas e a média ponderada.
* POST /api/evaluations registra seis notas inteiras e devolve a confirmação.
