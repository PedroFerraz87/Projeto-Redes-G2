# Projeto-Redes-G2

Implementação de comunicação cliente–servidor em TCP com handshake inicial negociando modo de operação (Go-Back-N ou Repetição Seletiva) e tamanho máximo de mensagem.

## Requisitos

- Python 3.10 ou superior (recomendado)
- Nenhuma dependência externa além da biblioteca padrão

## Estrutura do projeto

| Caminho | Descrição |
|---------|-----------|
| `src/server.py` | Servidor TCP que valida o handshake e responde com confirmação ou erro |
| `src/client.py` | Cliente que envia modo e tamanho máximo no início da conexão |
| `src/protocol.py` | Mensagens JSON do handshake (`handshake_init` / `handshake_ack`) |
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
cd src
python3 client.py --mode GBN --max-msg-size 64
```

Troque `GBN` por `SR` se quiser Repetição Seletiva, e `64` por outro inteiro **≥ 30**. **Não use** os símbolos `<` e `>` na linha de comando — no terminal (zsh/bash), `<` e `>` são operadores do shell; os valores devem ser escritos direto, como no exemplo acima.

**Parâmetros obrigatórios**

| Parâmetro | Valores | Significado |
|-----------|---------|-------------|
| `--mode` | `GBN` ou `SR` | `GBN` = Go-Back-N; `SR` = Repetição Seletiva |
| `--max-msg-size` | inteiro ≥ **30** | Tamanho máximo do texto negociado no handshake |

**Outros exemplos**

```bash
python3 client.py --mode SR --max-msg-size 128
python3 client.py --mode GBN --max-msg-size 30
```

Para ver a ajuda do cliente:

```bash
python3 client.py --help
```

## Fluxo da aplicação

1. O **cliente** conecta ao servidor.
2. O **cliente** envia uma mensagem JSON `handshake_init` com `mode` e `max_msg_size`.
3. O **servidor** valida e responde com `handshake_ack`: `status` (`ok` ou `error`), `window_size` e `message`.
4. Ambos exibem o conteúdo no terminal para verificação.

## Validações no servidor

- O tipo da primeira mensagem deve ser `handshake_init`.
- `mode` deve ser `GBN` ou `SR`.
- `max_msg_size` deve ser **no mínimo 30**.

Se algo for inválido, o servidor responde com `status: error` e `window_size: 0`.

## Observações

- Host e porta estão definidos no código (`127.0.0.1` e `5001`). Para testar em outra máquina, altere `HOST` (e eventualmente firewall) em `client.py` e `server.py` de forma consistente.
- O cliente deve ser executado **após** o servidor estar em execução; caso contrário, a conexão falhará.
