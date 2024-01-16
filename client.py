import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

def establish_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("Connection established with the server.")
    return client_socket

def send_request(client_socket, request):
    client_socket.send(request.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)

def list_files(client_socket):
    send_request(client_socket, 'LIST')

def download_file(client_socket, filename):
    send_request(client_socket, f'DOWNLOAD {filename}')
    response = client_socket.recv(BUFFER_SIZE)
    print(response.decode())

def upload_file(client_socket, filename, data):
    send_request(client_socket, f'UPLOAD {filename} {data}')
    response = client_socket.recv(BUFFER_SIZE)
    print(response.decode())

def delete_file(client_socket, filename):
    send_request(client_socket, f'DELETE {filename}')
    response = client_socket.recv(BUFFER_SIZE)
    print(response.decode())

def main():
    client_socket = establish_connection()

    list_files(client_socket)
    download_file(client_socket, 'example.txt')
    upload_file(client_socket, 'new_file.txt', 'This is a new file content.')
    delete_file(client_socket, 'new_file.txt')

    client_socket.close()

if __name__ == "__main__":
    main()
