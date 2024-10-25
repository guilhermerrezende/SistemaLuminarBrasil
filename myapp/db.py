import os
from psycopg2 import pool

# Carregar as configurações do banco de dados de variáveis de ambiente para flexibilidade
DATABASE = os.getenv('DB_NAME', 'postgres')
USER = os.getenv('DB_USER', 'postgres')
PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
HOST = os.getenv('DB_HOST', 'localhost')
PORT = os.getenv('DB_PORT', '5432')

# Inicializar o pool de conexões apenas se houver configurações válidas para o banco
connection_pool = None
if all([DATABASE, USER, PASSWORD, HOST, PORT]):
    try:
        connection_pool = pool.SimpleConnectionPool(
            1, 20,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )
    except Exception as e:
        print(f"Erro ao configurar o pool de conexões: {e}")

def get_connection():
    """Retorna uma conexão do pool, se ele estiver configurado."""
    if connection_pool:
        return connection_pool.getconn()
    else:
        raise Exception("Pool de conexões não está configurado. Verifique as configurações de ambiente.")

def put_connection(connection):
    """Devolve a conexão para o pool, se ele estiver configurado."""
    if connection_pool:
        connection_pool.putconn(connection)
    else:
        raise Exception("Pool de conexões não está configurado.")
