import socket
import os
import json

SERVER_IP = '192.168.56.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
CLIENT_DIR = './client_files/'

def establish_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    # O cliente deve se conectar com o servidor no IP e porta determinados, e ambos devem sinalizar que a conexão foi estabelecida com sucesso
    request = {'tipo_requisicao': 'ESTABLISHING_CONNECTION'}
    send_request(client_socket, request)
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)
    print("Client has connected with the server.")
    return client_socket

#Serializa os dados em JSON e envia ao servidor
def send_request(client_socket, request):
    json_data = json.dumps(request)
    client_socket.send(json_data.encode())

#O cliente deve poder fazer a listagem dos arquivos disponíveis no servidor
def list_files(client_socket):
    request = {'tipo_requisicao': 'LIST'}
    send_request(client_socket, request)
    response = client_socket.recv(BUFFER_SIZE).decode()
    json_response = json.loads(response)
    if 'files' in json_response and json_response['status'] == 'success':
        # Itera sobre a lista de arquivos e imprime cada nome de arquivo em uma nova linha
        for file_name in json_response['files']:
            print(file_name)
    else:
        print('The server directory does not contain any files.')

#O cliente deve poder deletar algum arquivo no servidor
def delete_file(client_socket, filename):
    send_request(client_socket, {'tipo_requisicao': 'DELETE', 'nome_arquivo': filename})
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)

#O cliente deve poder fazer um download de algum arquivo do servidor
def download_file(client_socket, filename, destination_folder):
    # Envia o comando de download ao servidor
    send_request(client_socket, {'tipo_requisicao': 'DOWNLOAD', 'nome_arquivo': filename})
    json_response = client_socket.recv(BUFFER_SIZE).decode()
    response = json.loads(json_response)
    status=response.get('status','')
    message=response.get('message','')
    print(json_response)
    if status == 'error':
        print(f"Error during download of file '{filename}': {message}")
        return
    # Cria o caminho completo para o arquivo de destino
    file_path = os.path.join(destination_folder, filename)
    try:
        # Recebe os dados do servidor em blocos e escreve no arquivo local
        with open(file_path, 'wb') as file:
            #print('Receiving data...')
            while True:
                #print('...Receiving data...')
                data = client_socket.recv(BUFFER_SIZE)
                #print(data)
                if not data:
                    #print('All data has been received...')
                    break
                
                if data.endswith(b"__end_of_file__"):
                    #não escreve '__end_of_file__' no arquivo
                    data = data[:-len(b"__end_of_file__")]
                    #print('...All data has been received...')
                    file.write(data)
                    # Todos os dados foram recebidos
                    break

                file.write(data)
        print(f"Download of file '{filename}' completed. Saved in '{destination_folder}'.")

    except Exception as e:
        print(f"Error during download of file '{filename}': {str(e)}")



#O cliente deve poder fazer upload de algum arquivo para o servidor
def upload_file(client_socket, filename, source_folder):
    file_path = os.path.join(source_folder, filename)
    # Envia o comando de upload
    if os.path.exists(file_path):
        print(f'File exists: {file_path}')
    else:
        print(f'File does not exist: {file_path}')
        return
    send_request(client_socket, {'tipo_requisicao': 'UPLOAD', 'nome_arquivo': filename})
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)
    try:
        # Abre o arquivo em modo binário
        with open(file_path, 'rb') as file:
            # Lê e envia os dados do arquivo em blocos
            while True:
                data = file.read(BUFFER_SIZE)
                #print(data)
                if not data:
                    # Todos os dados foram lidos
                    break
                client_socket.send(data)
        
        # Indicar ao servidor que a transmissão está completa
        client_socket.send(b"__end_of_file__")

    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except Exception as e:
        print(f"Error during download of file '{filename}': {str(e)}")

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
