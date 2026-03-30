import socket
from protocol import create_handshake_init, parse_message
from utils import send_message, receive_message

HOST = "127.0.0.1"
PORT = 5001


def main():
    mode = "GBN"
    max_msg_size = 30

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        print(f"Conectando ao servidor {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
        print("Conexão estabelecida com sucesso.")

        handshake_message = create_handshake_init(mode, max_msg_size)

        print("Enviando handshake:")
        print(handshake_message)

        send_message(client_socket, handshake_message)

        response_raw = receive_message(client_socket)
        response = parse_message(response_raw)

        print("Resposta recebida do servidor:")
        print(response)


if __name__ == "__main__":
    main()