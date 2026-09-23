import mysql.connector
from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from Models.productos import ProductoCreate, ProductoUpdate

router = APIRouter(prefix="/api/productos", tags=["Productos"])

@router.get("")
def listar_productos():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno al consultar la base de datos.")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion and conexion.is_connected():
            conexion.close()

@router.get("/codigo/{codigo}")
def obtener_producto_por_codigo(codigo: str):
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion and conexion.is_connected():
            conexion.close()

@router.post("", status_code=201)
def crear_producto(producto: ProductoCreate):
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
        if err.errno == 1062:  # Código de error MySQL para duplicados (UNIQUE)
            raise HTTPException(status_code=400, detail="El código de barras ya está registrado.")
        print(f"Error MySQL: {err}")
        raise HTTPException(status_code=500, detail="Error al registrar el producto.")
    except Exception as e:
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno al registrar el producto.")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion and conexion.is_connected():
            conexion.close()

@router.put("/{id_producto}")
def actualizar_producto(id_producto: int, producto: ProductoUpdate):
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
        if err.errno == 1062:
            raise HTTPException(status_code=400, detail="El código de barras ya pertenece a otro producto.")
        print(f"Error MySQL: {err}")
        raise HTTPException(status_code=500, detail="Error al actualizar el producto.")
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar el producto.")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion and conexion.is_connected():
            conexion.close()

@router.delete("/{id_producto}")
def eliminar_producto(id_producto: int):
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
        print(f"Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar el producto.")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion and conexion.is_connected():
            conexion.close()