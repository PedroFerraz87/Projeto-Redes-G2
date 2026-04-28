# Projeto-Redes-G2

Implementação de comunicação cliente–servidor em TCP com handshake inicial negociando modo de operação (Go-Back-N ou Repetição Seletiva) e tamanho máximo de mensagem, seguido de envio de mensagem fragmentada com janela deslizante e reconstrução no servidor.

## Requisitos

- Python 3.10 ou superior (recomendado)
- Nenhuma dependência externa além da biblioteca padrão

## Estrutura do projeto

| Caminho | Descrição |
|---------|-----------|
| `src/server.py` | Servidor TCP que valida o handshake, recebe pacotes, envia ACKs e reconstrói a mensagem |
| `src/client.py` | Cliente que negocia o handshake, fragmenta a mensagem e envia com janela deslizante |
| `src/protocol.py` | Definição das mensagens JSON do protocolo (`handshake_init`, `handshake_ack`, `data_packet`, `ack`, `message_reconstructed`) |
| `src/utils.py` | Envio e recebimento de dados no socket |

## Como executar

Abra **dois** terminais na pasta raiz do repositório.

### 1. Iniciar o servidor

```bash
cd src
python3 server.py
```

O servidor escuta em `127.0.0.1` na porta **5001** e aguarda uma conexão.

### 2. Iniciar o cliente

Em outro terminal (com o **servidor já rodando**):

```bash
python3 client.py --mode GBN --max-msg-size 64
```

Troque `GBN` por `SR` se quiser Repetição Seletiva, e `64` por outro inteiro **≥ 30**. **Não use** os símbolos `<` e `>` na linha de comando — no terminal (zsh/bash), `<` e `>` são operadores do shell; os valores devem ser escritos direto, como no exemplo acima.

Você também pode passar a mensagem diretamente pela linha de comando:

```bash
python3 client.py --mode GBN --max-msg-size 64 --message "Olá, mundo!"
```

Se `--message` for omitido, o terminal solicitará a mensagem interativamente.

**Parâmetros**

| Parâmetro | Obrigatório | Valores | Significado |
|-----------|-------------|---------|-------------|
| `--mode` | Sim | `GBN` ou `SR` | `GBN` = Go-Back-N; `SR` = Repetição Seletiva |
| `--max-msg-size` | Sim | inteiro ≥ **30** | Tamanho máximo de cada fragmento negociado no handshake |
| `--message` | Não | qualquer texto | Mensagem a ser enviada (se omitido, solicitada no terminal) |

**Outros exemplos**

```bash
python3 client.py --mode SR --max-msg-size 128
python3 client.py --mode GBN --max-msg-size 30 --message "Mensagem de teste"
```

Para ver a ajuda do cliente:

```bash
python3 client.py --help
```

## Fluxo da aplicação

1. O **cliente** conecta ao servidor via TCP.
2. O **cliente** envia `handshake_init` com `mode` e `max_msg_size`.
3. O **servidor** valida e responde com `handshake_ack`: `status` (`ok` ou `error`), `window_size` e `message`.
4. Se o handshake for aceito, o **cliente** fragmenta a mensagem em pacotes do tamanho negociado.
5. O **cliente** envia os pacotes usando janela deslizante de tamanho `window_size`, respeitando o modo negociado (GBN ou SR).
6. O **servidor** recebe cada pacote, envia um `ack` individual e armazena o fragmento.
7. Ao receber todos os fragmentos, o **servidor** reconstrói a mensagem e envia `message_reconstructed` ao cliente.
8. O **cliente** exibe a mensagem reconstruída recebida do servidor.

## Mensagens do protocolo

| Tipo | Enviado por | Descrição |
|------|-------------|-----------|
| `handshake_init` | Cliente | Inicia a negociação com `mode` e `max_msg_size` |
| `handshake_ack` | Servidor | Confirma ou recusa o handshake com `status`, `window_size` e `message` |
| `data_packet` | Cliente | Fragmento da mensagem com `seq`, `total` e `data` |
| `ack` | Servidor | Confirmação de recebimento do pacote com `seq` |
| `message_reconstructed` | Servidor | Mensagem completa reconstruída enviada ao cliente |

## Validações no servidor

- O tipo da primeira mensagem deve ser `handshake_init`.
- `mode` deve ser `GBN` ou `SR`.
- `max_msg_size` deve ser **no mínimo 30**.

Se algo for inválido, o servidor responde com `status: error` e `window_size: 0` e encerra a conexão.

## Observações

- Host e porta estão definidos no código (`127.0.0.1` e `5001`). Para testar em outra máquina, altere `HOST` em `client.py` e `server.py` de forma consistente.
- O cliente deve ser executado **após** o servidor estar em execução; caso contrário, a conexão falhará.
- O canal de comunicação simulado é perfeito — sem erros ou perdas de pacotes. O mecanismo de retransmissão por timeout está presente no cliente mas não será acionado neste cenário.