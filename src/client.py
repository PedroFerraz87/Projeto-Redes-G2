import argparse
import socket
from protocol import create_handshake_init, parse_message
from utils import send_message, receive_message

HOST = "127.0.0.1"
PORT = 5001


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cliente: modo (Go-Back-N ou Repetição Seletiva) e tamanho máximo "
        "são negociados no handshake, não fixos no código."
    )
    parser.add_argument(
        "--mode",
        choices=["GBN", "SR"],
        required=True,
        help="GBN = Go-Back-N, SR = Repetição Seletiva",
    )
    def min_msg_size(value):
        n = int(value)
        if n < 30:
            raise argparse.ArgumentTypeError("deve ser no mínimo 30")
        return n

    parser.add_argument(
        "--max-msg-size",
        type=min_msg_size,
        required=True,
        metavar="N",
        help="Tamanho máximo do texto (mínimo 30, conforme validação do servidor)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    mode = args.mode
    max_msg_size = args.max_msg_size

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