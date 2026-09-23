import mysql.connector
from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from pydantic import BaseModel
from typing import Optional

class ProductoSchema(BaseModel):
    codigoBarras: str
    nombreProducto: str
    categoriaProducto: Optional[str] = "General"
    precioCosto: Optional[float] = 0.0
    precioValor: float
    stockActual: int
    stockMinimo: Optional[int] = 5

router = APIRouter(prefix="/api/productos", tags=["Productos"])

def obtener_mapeo_columnas(cursor):
    """Detecta los nombres reales de las columnas en la tabla 'producto'"""
    cursor.execute("DESCRIBE producto")
    cols = [row["Field"] for row in cursor.fetchall()]
    
    return {
        "id": "idProducto" if "idProducto" in cols else "id",
        "codigo": "codigo" if "codigo" in cols else ("codigo_barras" if "codigo_barras" in cols else "codigoBarras"),
        "nombre": "nombre" if "nombre" in cols else ("nombreProducto" if "nombreProducto" in cols else "nombre_producto"),
        "categoria": "categoria" if "categoria" in cols else ("categoriaProducto" if "categoriaProducto" in cols else "categoria_producto"),
        "costo": "precioCosto" if "precioCosto" in cols else ("precio_costo" if "precio_costo" in cols else "costo"),
        "precio": "precio" if "precio" in cols else ("precioValor" if "precioValor" in cols else "precio_valor"),
        "stock": "stockActual" if "stockActual" in cols else ("stock_actual" if "stock_actual" in cols else "stock"),
        "stock_min": "stockMinimo" if "stockMinimo" in cols else ("stock_minimo" if "stock_minimo" in cols else "stockMinimo")
    }

@router.get("")
def listar_productos():
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        m = obtener_mapeo_columnas(cursor)
        
        query = f"""
            SELECT 
                {m['id']} AS idProducto,
                {m['codigo']} AS codigoBarras,
                {m['nombre']} AS nombreProducto,
                {m['categoria']} AS categoriaProducto,
                {m['costo']} AS precioCosto,
                {m['precio']} AS precioValor,
                {m['stock']} AS stockActual,
                {m['stock_min']} AS stockMinimo
            FROM producto 
            ORDER BY {m['id']} DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al listar productos: {e}")
        raise HTTPException(status_code=500, detail=f"Error BD: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

@router.post("", status_code=201)
def crear_producto(producto: ProductoSchema):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        m = obtener_mapeo_columnas(cursor)
        
        query = f"""
            INSERT INTO producto 
            ({m['codigo']}, {m['nombre']}, {m['categoria']}, {m['costo']}, {m['precio']}, {m['stock']}, {m['stock_min']})
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
        return {"mensaje": "Producto creado exitosamente", "idProducto": cursor.lastrowid}
    except mysql.connector.Error as err:
        if conexion and conexion.is_connected(): conexion.rollback()
        if err.errno == 1062:
            raise HTTPException(status_code=400, detail="El código de barras ya está registrado.")
        raise HTTPException(status_code=500, detail=f"Error en MySQL: {err.msg}")
    except Exception as e:
        if conexion and conexion.is_connected(): conexion.rollback()
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
        cursor = conexion.cursor(dictionary=True)
        m = obtener_mapeo_columnas(cursor)
        
        query = f"""
            UPDATE producto 
            SET {m['codigo']} = %s, {m['nombre']} = %s, {m['categoria']} = %s, 
                {m['costo']} = %s, {m['precio']} = %s, {m['stock']} = %s, {m['stock_min']} = %s
            WHERE {m['id']} = %s
        """
        valores = (
            producto.codigoBarras, producto.nombreProducto, producto.categoriaProducto,
            producto.precioCosto, producto.precioValor, producto.stockActual, producto.stockMinimo, id_producto
        )
        cursor.execute(query, valores)
        conexion.commit()
        return {"mensaje": f"Producto con ID {id_producto} actualizado correctamente"}
    except Exception as e:
        if conexion and conexion.is_connected(): conexion.rollback()
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
        cursor = conexion.cursor(dictionary=True)
        m = obtener_mapeo_columnas(cursor)
        
        cursor.execute(f"DELETE FROM producto WHERE {m['id']} = %s", (id_producto,))
        conexion.commit()
        return {"mensaje": f"Producto eliminado correctamente"}
    except Exception as e:
        if conexion and conexion.is_connected(): conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()<