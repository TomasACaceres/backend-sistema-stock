from pydantic import BaseModel, Field
from typing import List

class DetalleVentaItem(BaseModel):
    idProducto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precioUnitario: float = Field(..., gt=0)

class VentaCreate(BaseModel):
    idUsuario: int = Field(..., gt=0)
    metodoPago: str = Field(..., min_length=2)
    detalles: List[DetalleVentaItem] = Field(..., min_items=1) # Debe tener al menos 1 producto