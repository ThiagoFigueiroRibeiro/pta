import socket
import os

# Função para carregar clientes válidos de um arquivo .txt
def load_valid_clients(file_path):
    try:
        with open(file_path, 'r') as f:
            clients = [line.strip() for line in f.readlines()]
        return clients
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado.")
        return []

# Função para listar arquivos disponíveis em um diretório
def load_server_files(directory_path):
    try:
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        return files
    except FileNotFoundError:
        print(f"Diretório {directory_path} não encontrado.")
        return []

# Configurações do servidor
HOST = 'localhost'
PORT = 11550
CLIENTS_FILE = './pta-server/users.txt'  # Arquivo contendo os clientes válidos
FILES_DIR = './pta-server/files/'   # Diretório contendo os arquivos disponíveis
valid_clients = load_valid_clients(CLIENTS_FILE)
server_files = load_server_files(FILES_DIR)
state = "DISCONNECTED"  # Estado inicial
processing_file = False  # Para garantir atomicidade das operações de arquivos

def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    global state
    global processing_file  # Para garantir atomicidade nas operações de arquivos
    state = "WAITING_CUMP"  # Mudar para o estado de espera do CUMP
    client_validated = False
    seq_num_expected = 0
    
    try:
        while True:
            data = conn.recv(1024).decode('ascii')
            if not data:
                break
            print(f"Recebido: {data}")

            parts = data.split()
            if len(parts) < 2:
                conn.sendall(f"{seq_num_expected} NOK".encode('ascii'))
                break

            seq_num = int(parts[0])
            command = parts[1]
            args = parts[2] if len(parts) > 2 else None

            # Verificar o número de sequência
            if seq_num != seq_num_expected:
                conn.sendall(f"{seq_num} NOK".encode('ascii'))
                break
            seq_num_expected += 1

            # Fase de CUMP - Apresentação do cliente
            if state == "WAITING_CUMP":
                if command == "CUMP" and args:
                    if args in valid_clients:
                        client_validated = True
                        state = "READY"
                        conn.sendall(f"{seq_num} OK".encode('ascii'))
                    else:
                        conn.sendall(f"{seq_num} NOK".encode('ascii'))
                        conn.close()  # Fechar a conexão ao enviar NOK na validação
                        return
                else:
                    conn.sendall(f"{seq_num} NOK".encode('ascii'))
                    conn.close()  # Fechar a conexão se o comando não for CUMP
                    return

            elif state == "READY":
                # Comando LIST - listar arquivos
                if command == "LIST":
                    if processing_file:
                        conn.sendall(f"{seq_num} NOK".encode('ascii'))  # Garantir atomicidade
                    else:
                        try:
                            file_list = ','.join(server_files)
                            conn.sendall(f"{seq_num} ARQS {len(server_files)} {file_list}".encode('ascii'))
                        except Exception:
                            conn.sendall(f"{seq_num} NOK".encode('ascii'))

                # Comando PEGA - pegar arquivo
                elif command == "PEGA" and args:
                    if processing_file:
                        conn.sendall(f"{seq_num} NOK".encode('ascii'))  # Garantir atomicidade
                    else:
                        if args in server_files:
                            try:
                                processing_file = True  # Iniciar a operação atômica
                                file_path = os.path.join(FILES_DIR, args)
                                file_size = os.path.getsize(file_path)
                                with open(file_path, 'rb') as f:
                                    file_content = f.read()
                                conn.sendall(f"{seq_num} ARQ {file_size} ".encode('ascii') + file_content)
                            except Exception:
                                conn.sendall(f"{seq_num} NOK".encode('ascii'))
                            finally:
                                processing_file = False  # Liberar a operação atômica
                        else:
                            conn.sendall(f"{seq_num} NOK".encode('ascii'))

                # Comando TERM - fechamento da conexão
                elif command == "TERM":
                    conn.sendall(f"{seq_num} OK".encode('ascii'))
                    break

                # Comando desconhecido
                else:
                    conn.sendall(f"{seq_num} NOK".encode('ascii'))
                    
            else:
                conn.sendall(f"{seq_num} NOK".encode('ascii'))
                break

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

# Função principal para iniciar o servidor
def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor ouvindo na porta {PORT}...")

        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == '__main__':
    run_server()
