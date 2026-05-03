import argparse
import socket
from protocol import create_data_packet, create_handshake_init, parse_message
from utils import send_message, receive_message

HOST = "127.0.0.1"
PORT = 5001
MAX_PAYLOAD_SIZE = 4  # limite de 4 caracteres por pacote


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
    parser.add_argument(
        "--message",
        help="Mensagem a ser enviada após o handshake (se omitido, será solicitada no terminal).",
    )
    return parser.parse_args()


def fragment_message(message: str):
    return [message[i:i + MAX_PAYLOAD_SIZE] for i in range(0, len(message), MAX_PAYLOAD_SIZE)]


def send_with_window(sock, fragments, window_size: int, mode: str):
    total = len(fragments)
    next_seq = 0
    base = 0
    acked = set()
    sock.settimeout(3)

    while base < total:
        while next_seq < total and next_seq < base + window_size:
            packet = create_data_packet(next_seq, total, fragments[next_seq])
            send_message(sock, packet)
            print(f"[ENVIADO] seq={next_seq} | payload='{fragments[next_seq]}' | tamanho={len(fragments[next_seq])} chars | janela=[{base}, {min(base + window_size - 1, total - 1)}]")
            next_seq += 1

        try:
            raw_ack = receive_message(sock)
            if not raw_ack:
                raise ConnectionError("Conexão encerrada durante recebimento de ACK.")
            ack = parse_message(raw_ack)

            if ack.get("type") != "ack":
                continue

            ack_seq = ack.get("seq")
            if not isinstance(ack_seq, int):
                continue

            print(f"[ACK RECEBIDO] seq={ack_seq} | modo={mode} | base_atual={base}")

            if mode == "GBN":
                if ack_seq >= base:
                    base = ack_seq + 1
            else:
                acked.add(ack_seq)
                while base in acked:
                    base += 1
        except socket.timeout:
            if mode == "GBN":
                print(f"[TIMEOUT GBN] Reenviando todos os pacotes da janela a partir de seq={base}")
                next_seq = base
            else:
                print(f"[TIMEOUT SR] Reenviando apenas pacotes sem ACK na janela.")
                window_end = min(base + window_size, total)
                for seq in range(base, window_end):
                    if seq in acked:
                        continue
                    packet = create_data_packet(seq, total, fragments[seq])
                    send_message(sock, packet)
                    print(f"[REENVIO SR] seq={seq} | payload='{fragments[seq]}'")
    sock.settimeout(None)


def main():
    args = parse_args()
    mode = args.mode
    max_msg_size = args.max_msg_size
    message = args.message or input("Digite a mensagem para enviar: ").strip()

    if not message:
        raise ValueError("A mensagem não pode ser vazia.")

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

        if response.get("status") != "ok":
            print("Servidor recusou handshake. Encerrando cliente.")
            return

        window_size = response.get("window_size", 1)
        fragments = fragment_message(message)
        print(f"Mensagem fragmentada em {len(fragments)} pacote(s) de até {MAX_PAYLOAD_SIZE} caracteres cada.")

        send_with_window(client_socket, fragments, window_size, mode)

        reconstructed_raw = receive_message(client_socket)
        reconstructed = parse_message(reconstructed_raw)
        if reconstructed.get("type") == "message_reconstructed":
            print("Mensagem final recebida do servidor:")
            print(reconstructed.get("message"))
        else:
            print("Resposta final inesperada do servidor:")
            print(reconstructed)


if __name__ == "__main__":
    main()