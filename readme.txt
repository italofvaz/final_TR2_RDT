Descrição
Este programa implementa um protocolo de comunicação confiável chamado Go-Back-N, uma variação do protocolo de transferência de dados confiável (RDT). Ele é projetado para simular uma comunicação confiável sobre um canal de rede não confiável, lidando com perda de pacotes, corrupção de dados e reordenação.

Componentes
O programa consiste em três componentes principais:

Packet: Uma classe que define a estrutura dos pacotes de dados, incluindo a lógica para verificar a corrupção dos pacotes.

NetworkLayer: Uma abstração da camada de rede que simula um canal de comunicação não confiável, capaz de perda de pacotes, corrupção de dados e reordenação.

RDT (Reliable Data Transfer): A classe que implementa a lógica do protocolo Go-Back-N, incluindo o envio (rdt_4_0_send) e recebimento (rdt_4_0_receive) de pacotes de maneira confiável.

Pré-requisitos
Python 3.x
Conhecimento básico em redes de computadores e protocolos de comunicação.
Instruções de Uso
Configuração
Importe as Classes: Certifique-se de que as classes Packet, NetworkLayer e RDT estão no mesmo diretório e importadas corretamente em seu script principal.

Defina as Configurações da Rede: No script principal, configure as probabilidades de perda de pacote, corrupção e reordenação na criação do objeto NetworkLayer.

Executando o Programa
O programa pode ser executado em dois modos: Cliente e Servidor. Cada um desses modos é responsável por enviar e receber mensagens.

Para executar o código inicial, executar:

1) python3 server.py 5000
2) python3 client.py localhost 5000

Alunos: Italo Franklin, João Marcos Melo, José Marcos Gois