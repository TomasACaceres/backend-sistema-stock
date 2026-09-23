from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import obtener_conexion
import mysql.connector

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str | None = None
    dni: str | None = None

@router.get("", status_code=200)
def obtener_clientes():
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idCliente, nombre, telefono, dni, saldo FROM clientes ORDER BY idCliente DESC")
        clientes = cursor.fetchall()
        return clientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: 
            cursor.close()
        if conexion and conexion.is_connected(): 
            conexion.close()

@router.post("", status_code=201)
def crear_cliente(cliente: ClienteCreate):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        query = "INSERT INTO clientes (nombre, telefono, dni) VALUES (%s, %s, %s)"
        cursor.execute(query, (cliente.nombre, cliente.telefono, cliente.dni))
        conexion.commit()

        id_creado = cursor.lastrowid
        return {"exito": True, "idCliente": id_creado, "mensaje": "Cliente registrado correctamente."}
    except mysql.connector.Error as err:
        if conexion: 
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error en MySQL: {err.msg}")
    finally:
        if cursor: 
            cursor.close()
        if conexion and conexion.is_connected(): 
            conexion.close()

@router.delete("/{id_cliente}", status_code=200)
def eliminar_cliente(id_cliente: int):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM clientes WHERE idCliente = %s", (id_cliente,))
        conexion.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
            
        return {"exito": True, "mensaje": "Cliente eliminado."}
    except HTTPException as he:
        raise he
    except Exception as err:
        if conexion: 
            conexion.rollback()
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        if cursor: 
            cursor.close()
        if conexion and conexion.is_connected(): 
            conexion.close()