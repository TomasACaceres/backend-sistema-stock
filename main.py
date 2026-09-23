from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

# Importar routers
from Routers.productos import router as router_productos
from Routers.ventas import router as router_ventas
from Routers.clientes import router as router_clientes

# 1. Instanciar la aplicación
app = FastAPI(title="Sistema de Stock y Ventas API")

# 2. Configurar CORSuvicorn main:app --reload
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Registrar Routers
app.include_router(router_productos)
app.include_router(router_ventas)
app.include_router(router_clientes)

# Conexión a MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="proyecto-stock-ventas-caceresta3-0852.h.aivencloud.com",
        port=27198,
        user="avnadmin",
        password="AVNS_pPtJAnfFuVahbADPwFj",
        database="defaultdb",
        ssl_disabled=False
    )

# Schemas Pydantic
class UsuarioAuth(BaseModel):
    usuario: str
    password: str

@app.get("/")
def inicio():
    return {"mensaje": "API de Gestión de Stock y Ventas funcionando correctamente"}

# ==========================================
# ENDPOINTS DE AUTENTICACIÓN Y USUARIOS
# ==========================================

@app.post("/api/usuarios")
def registrar_usuario(datos: UsuarioAuth):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # 1. Verificar si el usuario ya existe
        cursor.execute("SELECT idUsuario FROM usuarios WHERE usuario = %s", (datos.usuario,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")

        # 2. Insertar el nuevo usuario
        query = "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)"
        cursor.execute(query, (datos.usuario, datos.password))
        db.commit()

        return {"exito": True, "mensaje": "Usuario registrado correctamente."}
    except mysql.connector.Error as err:
        print("Error de MySQL en Registro:", err)
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {err.msg}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

@app.post("/api/login")
def login_usuario(datos: UsuarioAuth):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # 1. Traer el usuario solo por nombre para verificar si existe
        query = "SELECT * FROM usuarios WHERE usuario = %s"
        cursor.execute(query, (datos.usuario,))
        usuario_encontrado = cursor.fetchone()

        cursor.close()
        db.close()

        # Si no existe el usuario
        if not usuario_encontrado:
            return {"exito": False, "mensaje": "Usuario o contraseña incorrectos."}

        # 2. Verificar la contraseña en Python
        pass_db = usuario_encontrado.get("password") or usuario_encontrado.get("clave") or usuario_encontrado.get("pass")

        if pass_db != datos.password:
            return {"exito": False, "mensaje": "Usuario o contraseña incorrectos."}

        return {
            "exito": True,
            "mensaje": "Inicio de sesión exitoso.",
            "usuario": usuario_encontrado["usuario"]
        }

    except Exception as err:
        print("\n==========================================")
        print("ERROR EN EL ENDPOINT LOGIN:", str(err))
        print("==========================================\n")
        return {"exito": False, "mensaje": f"Error interno: {str(err)}"}