import socket
import os
import threading

SERVER_IP = '192.168.56.1'
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
            #servidor deve suportar mais de uma conexão e operação simultânea de clientes
            #utilizando multithreading
            threading.Thread(target=handle_client, args=(client_socket,)).start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

def handle_client(client_socket):
    try:
        while True:
            request = client_socket.recv(BUFFER_SIZE).decode()
            if not request:
                break
            print("Request:")
            print(request)


            if request == 'LIST':
                response = list_files()
                client_socket.send(response.encode())
            elif request.startswith('DELETE'):
                _, filename = request.split(maxsplit=1)
                response = delete_file(filename)
                client_socket.send(response.encode())
            elif request.startswith('DOWNLOAD'):
                _, filename = request.split(maxsplit=1)
                send_file(client_socket, filename)
            elif request.startswith('UPLOAD'):
                _, filename = request.split(maxsplit=1)
                receive_file(client_socket, filename)

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

#usado para enviar o arquivo para o cliente, quando o cliente requisita download
def send_file(client_socket, filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        print(f'File exists: {file_path}')
    else:
        print(f'File does not exist: {file_path}')
    try:
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    # Todos os dados foram lidos
                    break
                client_socket.send(data)

        # Indicar ao cliente que a transmissão está completa
        client_socket.send(b"__end_of_file__")

        print(f"Download of '{filename}' completed.")

    except FileNotFoundError:
        print(f"File '{filename}' not found.")        
    except Exception as e:
        print(f"Error during download of file '{filename}': {str(e)}")

#usado para receber o arquivo do cliente, quando o cliente requisita upload
def receive_file(client_socket, filename):
    print(f"Receiving file '{filename}'...")
    file_path = os.path.join(BASE_DIR, filename)
    try:
        # Abre o arquivo no modo de escrita binária
        with open(file_path, 'wb') as file:
            # Recebe os dados do arquivo em blocos
            print('Receiving data...')
            while True:
                print('...Receiving data...')
                data = client_socket.recv(BUFFER_SIZE)
                print(data)
                if not data:
                    # Todos os dados foram recebidos
                    print('All data has been received...')
                    break
                
                if data.endswith(b"__end_of_file__"):
                    #não escreve '__end_of_file__' no arquivo
                    data = data[:-len(b"__end_of_file__")]
                    print('...All data has been received...')
                    file.write(data)
                    break

                file.write(data)

        print(f"Upload of file '{filename}' completed.")

    except Exception as e:
        print(f"Error during upload of file '{filename}': {str(e)}")


if __name__ == "__main__":
    start_server()
