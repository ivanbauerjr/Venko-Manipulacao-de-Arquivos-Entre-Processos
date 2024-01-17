import socket
import os

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
CLIENT_DIR = './client_files/'

def establish_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    # O cliente deve se conectar com o servidor no IP e porta determinados, e ambos devem sinalizar que a conexão foi estabelecida com sucesso
    print("Connection established with the server.")
    client_socket.send(''.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)
    return client_socket

def send_request(client_socket, request):
    client_socket.send(request.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)

#O cliente deve poder fazer a listagem dos arquivos disponíveis no servidor
def list_files(client_socket):
    send_request(client_socket, 'LIST')

#O cliente deve poder deletar algum arquivo no servidor
def delete_file(client_socket, filename):
    send_request(client_socket, f'DELETE {filename}')

#O cliente deve poder fazer um download de algum arquivo do servidor
def download_file(client_socket, filename, destination_folder):
    # Envia o comando de download ao servidor
    client_socket.send(f'DOWNLOAD {filename}'.encode())
    try:
        # Cria o caminho completo para o arquivo de destino
        file_path = os.path.join(destination_folder, filename)

        # Recebe os dados do servidor em blocos e escreve no arquivo local
        with open(file_path, 'wb') as file:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    # Todos os dados foram recebidos
                    break
                file.write(data)

        print(f"Download do arquivo '{filename}' concluído. Salvo em '{destination_folder}'.")

    except Exception as e:
        print(f"Erro durante o download do arquivo '{filename}': {str(e)}")



#O cliente deve poder fazer upload de algum arquivo para o servidor
def upload_file(client_socket, filename, source_folder):
    file_path = os.path.join(source_folder, filename)
    # Envia o comando de upload
    if os.path.exists(file_path):
        print(f'File exists: {file_path}')
    else:
        print(f'File does not exist: {file_path}')
    client_socket.send(f'UPLOAD {filename}'.encode())
    try:
        # Abre o arquivo em modo binário
        with open(file_path, 'rb') as file:
            # Lê e envia os dados do arquivo em blocos
            while True:
                data = file.read(BUFFER_SIZE)
                print(data)
                if not data:
                    # Todos os dados foram lidos
                    break
                client_socket.send(data)
        
        # Indicar ao servidor que a transmissão está completa
        #client_socket.send(b"__end_of_file__")

    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Erro durante o upload do arquivo '{filename}': {str(e)}")

def run_command(client_socket, command):
    if command == 'list':
        list_files(client_socket)

    elif command == 'delete':
        filename = input('Filename: ')
        delete_file(client_socket, filename)

    elif command == 'download':
        filename = input('Filename: ')
        download_file(client_socket, filename, CLIENT_DIR)

    elif command == 'upload':
        filename = input('Filename: ')
        upload_file(client_socket, filename, CLIENT_DIR)

    else:
        print('Invalid command.')
    
def main():
    client_socket = establish_connection()
    
    while True:
        #se a conexão for fechada, sair do loop
        if not client_socket:
            break

        print("\nAvailable commands:")
        print("download")
        print("upload")
        print("delete")
        print("list")
        print("exit\n")

        user_input = input("> ")
        if user_input.lower() == 'exit':
            break #encerra o loop se o usuário digitar 'exit'
        else:
            run_command(client_socket, user_input.lower())

    client_socket.close()

if __name__ == "__main__":
    main()
