# Venko-Manipulacao-de-Arquivos-Entre-Processos

O arquivo Documentação-Venko-Manipulacao-de-Arquivos-Entre-Processos.pdf, disponível no repositório, fornece a documentação do protocolo de comunicação entre cliente e servidor.
____________

Requisitos:

*Criar um canal de comunicação via socket entre dois processos no modelo cliente-servidor. 

*O Servidor deve disponibilizar uma funcionalidade bem básica para manipulação de arquivos e o cliente deve ter opção de listagem, deleção, download e upload dos arquivos em um diretório fixo no servidor.

*O Servidor deve suportar mais de uma conexão e operação simultânea de clientes.
*O Servidor deve abrir um socket para um endereço IP e porta fixos.

*O cliente deve se conectar com o servidor no IP e porta determinados, e ambos devem sinalizar que a conexão foi estabelecida com sucesso.
*O cliente deve poder fazer a listagem dos arquivos disponíveis no servidor.
*O cliente deve poder fazer um download de algum arquivo do servidor.
*O cliente deve poder deletar algum arquivo no servidor.
*O cliente deve poder fazer upload de algum arquivo para o servidor.

*A comunicação entre cliente e servidor deve ter uma estrutura de dados que atenda as operações listadas acima.
