from pydantic import BaseModel, Field

class ProductoBase(BaseModel):
    nombreProducto: str = Field(..., min_length=2, max_length=100)
    codigoBarras: str = Field(..., min_length=3, max_length=50)
    categoriaProducto: str = Field(..., min_length=2, max_length=50)
    precioCosto: float = Field(..., gt=0)   # Mayor a 0
    precioValor: float = Field(..., gt=0)   # Mayor a 0
    stockActual: int = Field(..., ge=0)     # Mayor o igual a 0
    stockMinimo: int = Field(default=5, ge=0)



class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass