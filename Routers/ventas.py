from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from pydantic import BaseModel
from typing import Optional, List

# Modelos Pydantic
class DetalleVenta(BaseModel):
    idProducto: int
    cantidad: int
    precio: float  # Coincide con la propiedad 'precio' enviada por el JS

class VentaCreate(BaseModel):
    idUsuario: Optional[int] = 1  # Por defecto 1
    idCliente: Optional[int] = None
    metodoPago: str
    detalles: List[DetalleVenta]
    total: Optional[float] = None

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])

@router.post("", status_code=201)
def registrar_venta(venta: VentaCreate):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Calculamos el total usando item.precio
        monto_total = sum(item.cantidad * item.precio for item in venta.detalles)
        id_usuario = venta.idUsuario if venta.idUsuario else 1

        # 1. Registrar la venta
        query_venta = """
            INSERT INTO venta (idUsuario, usuario_idUsuario, fechaVenta, totalVenta, metodoPago)
            VALUES (%s, %s, NOW(), %s, %s)
        """
        cursor.execute(query_venta, (id_usuario, id_usuario, monto_total, venta.metodoPago))
        id_venta = cursor.lastrowid

        # 2. Registrar el detalle y descontar stock
        for item in venta.detalles:
            cursor.execute("SELECT stockActual, nombreProducto FROM producto WHERE idProducto = %s", (item.idProducto,))
            prod = cursor.fetchone()

            if not prod:
                conexion.rollback()
                raise HTTPException(status_code=404, detail=f"El producto con ID {item.idProducto} no existe.")

            if prod["stockActual"] < item.cantidad:
                conexion.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{prod['nombreProducto']}'. Disponible: {prod['stockActual']}, Solicitado: {item.cantidad}"
                )

            # Descontar del inventario
            query_stock = "UPDATE producto SET stockActual = stockActual - %s WHERE idProducto = %s"
            cursor.execute(query_stock, (item.cantidad, item.idProducto))

            # Insertar en detalleventa usando item.precio
            query_detalle = """
                INSERT INTO detalleventa (venta_idVenta, producto_idProducto, cantidad, precioUnitario)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_detalle, (id_venta, item.idProducto, item.cantidad, item.precio))

        # 3. Si el pago es Fiado, sumar el saldo a la cuenta corriente del cliente
        if venta.metodoPago == "Fiado" and venta.idCliente:
            query_cliente = "UPDATE clientes SET saldo = saldo + %s WHERE idCliente = %s"
            cursor.execute(query_cliente, (monto_total, venta.idCliente))

        conexion.commit()
        return {"mensaje": "Venta registrada exitosamente", "idVenta": id_venta, "montoTotal": monto_total}

    except HTTPException as he:
        raise he
    except Exception as e:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la venta: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


@router.get("", status_code=200)
def obtener_historial_ventas():
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Convertimos fechaVenta a string ISO formateado desde MySQL
        query = """
            SELECT 
                idVenta, 
                DATE_FORMAT(fechaVenta, '%Y-%m-%dT%H:%i:%s') AS fechaVenta, 
                totalVenta, 
                metodoPago 
            FROM venta 
            ORDER BY idVenta DESC
        """
        cursor.execute(query)
        ventas = cursor.fetchall()
        return ventas

    except Exception as e:
        print(f"Error interno en historial de ventas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()