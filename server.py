import socket
import os
import threading
import json

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
            ''' 
            #Minha primeira implementação consistia em receber solicitações no formato de string <comando> <nome_arquivo>
            #Utilizei o método split(maxsplit=1) para separar o comando do nome do arquivo
            #Após conversar com o tutor, alterei para receber solicitações no formato JSON
            #Abaixo está a minha primeira implementação, comentada

            request = client_socket.recv(BUFFER_SIZE).decode()
            if not request:
                break
            #print("Request:")
            #print(request)

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
            '''

            # Recebe a string JSON do cliente
            json_request = client_socket.recv(BUFFER_SIZE).decode()

            if not json_request:
                break

            # Desserializa a string JSON para um dicionário Python
            try:
                # Tente desserializar a string JSON para um dicionário
                request_data = json.loads(json_request)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                # Em caso de erro de desserialização, envie uma mensagem de erro ao cliente
                error_response = {'status': 'error', 'message': 'Invalid JSON format.'}
                client_socket.send(json.dumps(error_response).encode())
                continue

            # Extraindo os campos relevantes do dicionário
            tipo_requisicao = request_data.get('tipo_requisicao', '')
            nome_arquivo = request_data.get('nome_arquivo', '')

            print("JSON_Request:")
            print(json_request)

            if tipo_requisicao == 'LIST':
                response = list_files()
                # Serializa a resposta em formato JSON antes de enviar ao cliente
                client_socket.send(json.dumps(response).encode())
            elif tipo_requisicao == 'DELETE':
                response = delete_file(nome_arquivo)
                client_socket.send(json.dumps(response).encode())
            elif tipo_requisicao == 'DOWNLOAD':
                send_file(client_socket, nome_arquivo)
            elif tipo_requisicao == 'UPLOAD':
                receive_file(client_socket, nome_arquivo)
            elif tipo_requisicao == 'ESTABLISHING_CONNECTION':
                # Cria um dicionário com a mensagem de sucesso
                message = {'status': 'success', 'message': 'Connection established.'}
                # Serializa o dicionário em formato JSON antes de enviar
                json_message = json.dumps(message)
                client_socket.send(json_message.encode())
                print("Connection established with the client.")
            else:
                print(f"Invalid request: {request_data}")
                response = {'status': 'error', 'message': 'Invalid request.'}
                client_socket.send(json.dumps(response).encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def list_files():
    files = os.listdir(BASE_DIR)
    # Se a lista de arquivos estiver vazia, retorna uma mensagem de erro
    if not files:
        return {'status': 'error', 'message': 'No files found.'}
    # Retorna um dicionário contendo a lista de arquivos
    return {'status': 'success','files': files}


def delete_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Retorna um dicionário indicando que o arquivo foi excluído com sucesso
        return {'status': 'success', 'message': 'File deleted successfully.'}
    else:
        # Retorna um dicionário indicando que o arquivo não foi encontrado
        return {'status': 'error', 'message': 'File not found.'}

#usado para enviar o arquivo para o cliente, quando o cliente requisita download
def send_file(client_socket, filename):
    file_path = os.path.join(BASE_DIR, filename)
    response = {'status': '', 'message': ''}

    if os.path.exists(file_path):
        response['status'] = 'success'
        response['message'] = 'File found. Transference started.'
        print(f'File exists: {file_path}')
        client_socket.send(json.dumps(response).encode())
    else:
        response['status'] = 'error'
        response['message'] = 'File not found.'
        print(f'File does not exist: {file_path}')
        client_socket.send(json.dumps(response).encode())
        return
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

        print(f"Transfer of '{filename}' completed.")
    
    except Exception as e:
        print(f"Error during transfer of file '{filename}': {str(e)}")

#usado para receber o arquivo do cliente, quando o cliente requisita upload
def receive_file(client_socket, filename):
    print(f"Receiving file '{filename}'...")
    file_path = os.path.join(BASE_DIR, filename)
    try:
        response = {'status': 'success', 'message': 'Receiving file...'}
        client_socket.send(json.dumps(response).encode())
        # Abre o arquivo no modo de escrita binária
        with open(file_path, 'wb') as file:
            # Recebe os dados do arquivo em blocos
            #print('Receiving data...')
            while True:
                #print('...Receiving data...')
                data = client_socket.recv(BUFFER_SIZE)
                #print(data)
                if not data:
                    # Todos os dados foram recebidos
                    print('All data has been received...')
                    break
                
                if data.endswith(b"__end_of_file__"):
                    #não escreve '__end_of_file__' no arquivo
                    data = data[:-len(b"__end_of_file__")]
                    #print('...All data has been received...')
                    file.write(data)
                    break

                file.write(data)

        print(f"Transfer of file '{filename}' completed.")

    except Exception as e:
        print(f"Error during transfer of file '{filename}': {str(e)}")
        response = {'status': 'error', 'message': 'Error during transfer of file.'}
        client_socket.send(json.dumps(response).encode())


if __name__ == "__main__":
    start_server()
