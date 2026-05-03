import socket
from protocol import create_ack, create_handshake_ack, create_message_reconstructed, parse_message
from utils import send_message, receive_message

HOST = "127.0.0.1"
PORT = 5001
INITIAL_WINDOW_SIZE = 5


def validate_handshake(data: dict):
    if data.get("type") != "handshake_init":
        return False, "Tipo de mensagem inválido"
    if data.get("mode") not in ["GBN", "SR"]:
        return False, "Modo de operação inválido"
    if data.get("max_msg_size", 0) < 30:
        return False, "O tamanho máximo deve ser no mínimo 30"
    return True, "Handshake realizado com sucesso"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"Servidor escutando em {HOST}:{PORT}...")
        print("Aguardando conexão do cliente...")

        conn, addr = server_socket.accept()

        with conn:
            print(f"Cliente conectado: {addr}")

            raw_data = receive_message(conn)
            data = parse_message(raw_data)

            print("Handshake recebido do cliente:")
            print(data)

            valid, message = validate_handshake(data)

            if valid:
                response = create_handshake_ack(
                    status="ok",
                    window_size=INITIAL_WINDOW_SIZE,
                    message=message
                )
                print("Handshake aceito.")
            else:
                response = create_handshake_ack(
                    status="error",
                    window_size=0,
                    message=message
                )
                print("Handshake recusado.")

            send_message(conn, response)
            print("Resposta enviada ao cliente.")

            if not valid:
                return

            mode = data.get("mode")
            fragments = {}
            total_expected = None
            expected_seq = 0

            while True:
                raw_packet = receive_message(conn)
                if not raw_packet:
                    print("Conexão encerrada antes da reconstrução completa.")
                    break

                packet = parse_message(raw_packet)
                if packet.get("type") != "data_packet":
                    print("Mensagem inesperada recebida; ignorando.")
                    continue

                seq = packet.get("seq")
                total = packet.get("total")
                data_payload = packet.get("data", "")
                if not isinstance(seq, int) or not isinstance(total, int):
                    print("Pacote inválido recebido; ignorando.")
                    continue

                total_expected = total if total_expected is None else total_expected

                if mode == "GBN":
                    if seq == expected_seq:
                        fragments[seq] = data_payload
                        expected_seq += 1
                        print(f"[GBN RECEBIDO] seq={seq} | payload='{data_payload}' | tamanho={len(data_payload)} chars | esperado_proximo={expected_seq}")
                    else:
                        print(f"[GBN DESCARTADO] seq={seq} | payload='{data_payload}' | esperado={expected_seq}")

                    ack_seq = expected_seq - 1
                    ack = create_ack(ack_seq)
                    send_message(conn, ack)
                    print(f"[GBN ACK ENVIADO] seq={ack_seq} | tipo=cumulativo")
                else:
                    fragments[seq] = data_payload
                    ack = create_ack(seq)
                    send_message(conn, ack)
                    print(f"[SR RECEBIDO] seq={seq} | payload='{data_payload}' | tamanho={len(data_payload)} chars")
                    print(f"[SR ACK ENVIADO] seq={seq} | tipo=individual")

                if total_expected is not None and len(fragments) == total_expected:
                    message = "".join(fragments[i] for i in range(total_expected))
                    final_response = create_message_reconstructed(message)
                    send_message(conn, final_response)
                    print(f"[RECONSTRUÇÃO] Mensagem completa: '{message}' | total_pacotes={total_expected}")
                    break


if __name__ == "__main__":
    main()