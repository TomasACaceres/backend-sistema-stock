import mysql.connector
from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from pydantic import BaseModel
from typing import Optional

# Definición directa y tolerante de los esquemas para evitar errores de validación 422
class ProductoSchema(BaseModel):
    codigoBarras: str
    nombreProducto: str
    categoriaProducto: Optional[str] = "General"
    precioCosto: Optional[float] = 0.0
    precioValor: float
    stockActual: int
    stockMinimo: Optional[int] = 5

router = APIRouter(prefix="/api/productos", tags=["Productos"])

@router.get("")
def listar_productos():
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto ORDER BY idProducto DESC")
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Error interno al listar productos: {e}")
        raise HTTPException(status_code=500, detail=f"Error BD: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

@router.get("/codigo/{codigo}")
def obtener_producto_por_codigo(codigo: str):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
            SELECT 
                idProducto, 
                codigoBarras AS codigo, 
                nombreProducto AS nombre, 
                precioValor AS precio, 
                stockActual AS stock 
            FROM producto 
            WHERE codigoBarras = %s
        """
        cursor.execute(query, (codigo,))
        producto = cursor.fetchone()

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        return producto
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

@router.post("", status_code=201)
def crear_producto(producto: ProductoSchema):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = """
            INSERT INTO producto (codigoBarras, nombreProducto, categoriaProducto, precioCosto, precioValor, stockActual, stockMinimo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            producto.codigoBarras,
            producto.nombreProducto,
            producto.categoriaProducto,
            producto.precioCosto,
            producto.precioValor,
            producto.stockActual,
            producto.stockMinimo
        )
        cursor.execute(query, valores)
        conexion.commit()
        nuevo_id = cursor.lastrowid
        return {"mensaje": "Producto creado exitosamente", "idProducto": nuevo_id}
    except mysql.connector.Error as err:
        if conexion and conexion.is_connected():
            conexion.rollback()
        if err.errno == 1062:
            raise HTTPException(status_code=400, detail="El código de barras ya está registrado.")
        print(f"Error MySQL: {err}")
        raise HTTPException(status_code=500, detail=f"Error en MySQL: {err.msg}")
    except Exception as e:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

@router.put("/{id_producto}")
def actualizar_producto(id_producto: int, producto: ProductoSchema):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = """
            UPDATE producto 
            SET codigoBarras = %s, nombreProducto = %s, categoriaProducto = %s, precioCosto = %s, 
                precioValor = %s, stockActual = %s, stockMinimo = %s
            WHERE idProducto = %s
        """
        valores = (
            producto.codigoBarras, producto.nombreProducto, producto.categoriaProducto, producto.precioCosto,
            producto.precioValor, producto.stockActual, producto.stockMinimo, id_producto
        )
        cursor.execute(query, valores)
        conexion.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"mensaje": f"Producto con ID {id_producto} actualizado correctamente"}
    except mysql.connector.Error as err:
        if conexion and conexion.is_connected():
            conexion.rollback()
        if err.errno == 1062:
            raise HTTPException(status_code=400, detail="El código de barras ya pertenece a otro producto.")
        print(f"Error MySQL: {err}")
        raise HTTPException(status_code=500, detail=f"Error en MySQL: {err.msg}")
    except HTTPException as he:
        raise he
    except Exception as e:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

@router.delete("/{id_producto}")
def eliminar_producto(id_producto: int):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE idProducto = %s", (id_producto,))
        conexion.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"mensaje": f"Producto con ID {id_producto} eliminado correctamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()