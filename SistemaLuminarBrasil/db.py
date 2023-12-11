import psycopg2
from psycopg2 import pool

DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '21788102'
HOST = 'luminar-1.c1tcpi4qrlgu.us-east-1.rds.amazonaws.com'
PORT = '5432'

# Configurar pool de conexão
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

def get_connection():
    return connection_pool.getconn()

def put_connection(connection):
    connection_pool.putconn(connection)
