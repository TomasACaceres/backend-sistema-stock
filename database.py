import os
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

load_dotenv()

# Variables con valores por defecto hacia Aiven si no existen en el .env
DB_HOST = os.getenv("DB_HOST", "proyecto-stock-ventas-caceresta3-0852.h.aivencloud.com")
DB_USER = os.getenv("DB_USER", "avnadmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "AVNS_pPtJAnfFuVahbADPwFj")
DB_NAME = os.getenv("DB_NAME", "defaultdb")
DB_PORT = int(os.getenv("DB_PORT", 27198))

try:
    # Pool de conexiones configurado con el puerto 27198 de Aiven
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="stock_pool",
        pool_size=5,
        pool_reset_session=True,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    print("Pool de conexiones inicializado correctamente.")
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