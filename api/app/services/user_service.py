from app.sql.queries import queries
from app.db import get_connection
import bcrypt
import random
from datetime import datetime

def insert_user(user):
    conn = get_connection()
    if conn is None:
        return {
            "status": "failed",
            "message": "No se pudo conectar a la base de datos"
        }, 500  # Internal Server Error
    
    # Verificar si faltan datos esenciales
    required_fields = ["cui", "nombre", "apellido", "correo", "telefono", "contrasena", "estado_sesion", "verificacion_correo"]
    for field in required_fields:
        if field not in user:
            return {
                "status": "failed",
                "message": f"Falta el campo requerido: {field}"
            }, 400  # Bad Request
    
    if user["estado_sesion"] not in ["TRUE", "FALSE"]:
        return {"status": "failed", "message": "estado_sesion debe ser TRUE o FALSE"}, 400
    
    if user["verificacion_correo"] not in ["FALSE", "TRUE"]:
        return {"status": "failed", "message": "verificacion_correo debe ser TRUE o FALSE"}, 400


    # Hashear la contraseña
    user["contrasena"] = hash_password(user["contrasena"])
    
    try:
        with conn.cursor() as cursor:
            # Verificar si el correo, cui o id_usuario ya existen en la base de datos
            cursor.execute(queries['check_email_exists'], {"correo": user["correo"]})
            if cursor.fetchone()[0] > 0:
                return {
                    "status": "failed",
                    "message": "El correo ya está en uso"
                }, 409  # Conflict

            cursor.execute(queries['check_cui_exists'], {"cui": user["cui"]})
            if cursor.fetchone()[0] > 0:
                return {
                    "status": "failed",
                    "message": "El CUI ya está en uso"
                }, 409  # Conflict

            # Insertar el nuevo usuario
            cursor.execute(queries["insert_user"], user)
            conn.commit()

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        conn.close()

    return {
        "status": "success",
        "message": "Usuario creado con éxito"
    }, 201  # Created




def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
