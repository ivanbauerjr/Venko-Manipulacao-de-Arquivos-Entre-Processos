import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

def establish_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    # O cliente deve se conectar com o servidor no IP e porta determinados, e ambos devem sinalizar que a conexão foi estabelecida com sucesso
    print("Connection established with the server.")
    return client_socket

def send_request(client_socket, request):
    client_socket.send(request.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)

#O cliente deve poder fazer a listagem dos arquivos disponíveis no servidor
def list_files(client_socket):
    send_request(client_socket, 'LIST')

#O cliente deve poder fazer um download de algum arquivo do servidor
def download_file(client_socket, filename):
    send_request(client_socket, f'DOWNLOAD {filename}')
    response = client_socket.recv(BUFFER_SIZE)
    print(response.decode())

#O cliente deve poder deletar algum arquivo no servidor
def delete_file(client_socket, filename):
    send_request(client_socket, f'DELETE {filename}')
    response = client_socket.recv(BUFFER_SIZE)
    print(response.decode())

#O cliente deve poder fazer upload de algum arquivo para o servidor
def upload_file(client_socket, filename, data):
    send_request(client_socket, f'UPLOAD {filename} {data}')
    response = client_socket.recv(BUFFER_SIZE)
    print(response.decode())

def run_command(client_socket, command):
    if command == 'download':
        filename = input('Filename: ')
        download_file(client_socket, filename)

    elif command == 'upload':
        filename = input('Filename: ')
        data = input('Data: ')
        upload_file(client_socket, filename, data)

    elif command == 'delete':
        filename = input('Filename: ')
        delete_file(client_socket, filename)

    elif command == 'list':
        list_files(client_socket)


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
