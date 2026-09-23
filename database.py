import os
import mysql.connector
from mysql.connector import pooling, Error
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

try:
    # Pool de conexiones para no abrir/cerrar sockets físicos en cada request
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="stock_pool",
        pool_size=5,
        pool_reset_session=True,
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "sistema_stock")
    )
except Error as e:
    print(f"Error al inicializar el pool de conexiones: {e}")
    raise e

def obtener_conexion():
    """Obtiene una conexión reutilizable del pool."""
    try:
        return db_pool.get_connection()
    except Error as e:
        print(f"Error al obtener conexión del pool: {e}")
        raise e