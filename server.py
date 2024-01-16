import socket
import os
import multiprocessing

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
BASE_DIR = './server_files/'

def list_files():
    files = os.listdir(BASE_DIR)
    return '\n'.join(files)

def download_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as file:
            return file.read()
    else:
        return b'File not found.'

def upload_file(filename, data):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'wb') as file:
        file.write(data)
    return 'File uploaded successfully.'

def delete_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return 'File deleted successfully.'
    else:
        return 'File not found.'

def handle_client(client_socket):
    try:
        while True:
            request = client_socket.recv(BUFFER_SIZE).decode()

            if not request:
                break

            if request == 'LIST':
                response = list_files()
            elif request.startswith('DOWNLOAD'):
                _, filename = request.split()
                response = download_file(filename)
            elif request.startswith('UPLOAD'):
                _, filename, data = request.split(maxsplit=2)
                response = upload_file(filename, data.encode())
            elif request.startswith('DELETE'):
                _, filename = request.split()
                response = delete_file(filename)
            else:
                response = 'Invalid request.'

            client_socket.send(response.encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

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
            client_handler = multiprocessing.Process(target=handle_client, args=(client_socket,))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
