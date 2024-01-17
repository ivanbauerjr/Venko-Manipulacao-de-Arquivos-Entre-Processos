import socket
import os
import multiprocessing

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
BASE_DIR = './server_files/'

def start_server():
    #socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Servidor deve abrir um socket para um endereço IP e porta fixos
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            ## O cliente deve se conectar com o servidor no IP e porta determinados, e ambos devem sinalizar que a conexão foi estabelecida com sucesso
            client_socket.send(b'Connection established.')
            #servidor suportar mais de uma conexão e operação simultânea de clientes
            #client_handler = multiprocessing.Process(target=handle_client, args=(client_socket,))
            #client_handler.start()

            #inicialmente testando com apenas um client
            handle_client(client_socket)

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

def handle_client(client_socket):
    try:
        while True:
            request = client_socket.recv(BUFFER_SIZE).decode()
            print("Request:")
            print(request)
            if not request:
                break

            if request == 'LIST':
                response = list_files()
                client_socket.send(response.encode())
            elif request.startswith('DELETE'):
                _, filename = request.split()
                response = delete_file(filename)
                client_socket.send(response.encode())
            elif request.startswith('DOWNLOAD'):
                _, filename = request.split()
                download_file(client_socket, filename)
                #response = download_file(client_socket, filename)
                #client_socket.send(response.encode())
            elif request.startswith('UPLOAD'):
                _, filename = request.split()
                upload_file(client_socket, filename)
                #response = upload_file(client_socket, filename, data.encode())
                #client_socket.send(response.encode())

            else:
                print(f"Invalid request: {request}")
                response = 'Invalid request.'
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def list_files():
    files = os.listdir(BASE_DIR)
    return '\n'.join(files)

def delete_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return 'File deleted successfully.'
    else:
        return 'File not found.'

#usado para enviar o arquivo para o cliente
def download_file(client_socket, filename):
    filepath = os.path.join(BASE_DIR, filename)
    try:
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    # Todos os dados foram lidos
                    break
                client_socket.send(data)

        # Indicar ao cliente que a transmissão está completa
        client_socket.send(b"__end_of_file__")

        print(f"Download do arquivo '{filename}' concluído.")

    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado.")        
    except Exception as e:
        print(f"Erro durante o download do arquivo '{filename}': {str(e)}")

#usado para receber o arquivo do cliente
def upload_file(client_socket, filename):
    print(f"Recebendo arquivo '{filename}'...")
    file_path = os.path.join(BASE_DIR, filename)
    try:
        # Abre o arquivo no modo de escrita binária
        with open(file_path, 'wb') as file:
            # Recebe os dados do arquivo em blocos
            print('Recebendo dados...')
            while True:
                print('...Recebendo dados...')
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    # Todos os dados foram recebidos
                    print('...Todos os dados foram recebidos...')
                    break
                file.write(data)

        print(f"Upload do arquivo '{filename}' concluído.")

    except Exception as e:
        print(f"Erro durante o upload do arquivo '{filename}': {str(e)}")


if __name__ == "__main__":
    start_server()
