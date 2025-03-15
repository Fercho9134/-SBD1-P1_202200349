from app.sql.queries import queriesUsuario
from app.db import get_connection
import bcrypt
from datetime import datetime

def insert_user(user):
    
    # Verificar si faltan datos esenciales
    required_fields = ["cui", "nombre", "apellido", "correo", "telefono", "contrasena"]

    for field in required_fields:
        if field not in user:
            return {
                "status": "failed",
                "message": f"Falta el campo requerido: {field}"
            }, 400  # Bad Request
        
    #Si estado_sesion y verificacion_correo no existen agregarlos con valores por defecto
    if "estado_sesion" not in user:
        user["estado_sesion"] = "TRUE"
    
    if "verificacion_correo" not in user:
        user["verificacion_correo"] = "FALSE"
    
    if user["estado_sesion"] not in ["TRUE", "FALSE"]:
        return {"status": "failed", "message": "estado_sesion debe ser TRUE o FALSE"}, 400
    
    if user["verificacion_correo"] not in ["FALSE", "TRUE"]:
        return {"status": "failed", "message": "verificacion_correo debe ser TRUE o FALSE"}, 400
    
    # Hashear la contraseña
    user["contrasena"] = hash_password(user["contrasena"])
    
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        with conn.cursor() as cursor:
            # Verificar si el correo, cui o id_usuario ya existen en la base de datos
            cursor.execute(queriesUsuario['check_email_exists'], {"correo": user["correo"]})
            if cursor.fetchone()[0] > 0:
                return {
                    "status": "failed",
                    "message": "El correo ya está en uso"
                }, 409  # Conflict

            cursor.execute(queriesUsuario['check_cui_exists'], {"cui": user["cui"]})
            if cursor.fetchone()[0] > 0:
                return {
                    "status": "failed",
                    "message": "El CUI ya está en uso"
                }, 409  # Conflict

            # Insertar el nuevo usuario
            cursor.execute(queriesUsuario["insert_user"], user)
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



def login_user(user):
    # Validar campos requeridos antes de conectarse a la base de datos
    required_fields = ["correo", "contrasena"]
    for field in required_fields:
        if field not in user or not user[field].strip():
            return {
                "status": "failed",
                "message": f"Falta el campo requerido: {field}"
            }, 400  # Bad Request

    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        with conn.cursor() as cursor:
            # Buscar el hash de la contraseña y el ID del usuario
            cursor.execute(queriesUsuario["get_password"], {"correo": user["correo"].strip()})
            result = cursor.fetchone()
            if result is None:
                return {
                    "status": "failed",
                    "message": "El correo no está registrado"
                }, 401  # Unauthorized
            
            id_usuario, hashed_password = result

            # Verificar la contraseña con bcrypt
            if not verify_password(user["contrasena"], hashed_password):
                return {
                    "status": "failed",
                    "message": "Contraseña incorrecta"
                }, 401  # Unauthorized

            # Obtener datos del usuario
            cursor.execute(queriesUsuario["get_user"], {"id_usuario": id_usuario})
            result = cursor.fetchone()

            if result is None:
                return {
                    "status": "failed",
                    "message": "Error al recuperar los datos del usuario"
                }, 500  # Internal Server Error

            usuario = {
                "id_usuario": result[0],
                "nombre": result[2],
                "apellido": result[3],
            }

            return {
                "status": "success",
                "message": f"El usuario {usuario['nombre']} {usuario['apellido']} con ID {usuario['id_usuario']} ha iniciado sesión",
                "user": usuario
            }, 200  # OK

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        conn.close()

    

def obtener_usuario(id_usuario=None):

    if id_usuario is None or not id_usuario:
        return {
            "status": "failed",
            "message": "Falta el ID del usuario"
        }, 400  # Bad Request

    try:

        conn = get_connection()
        if conn is None:
            return {
            "status": "failed",
            "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
    
        with conn.cursor() as cursor:
            cursor.execute(queriesUsuario["get_user"], {"id_usuario": id_usuario})
            result = cursor.fetchone()

            if result is None:
                return {
                    "status": "failed",
                    "message": "Usuario no encontrado"
                }, 404  # Not Found

            usuario = {
                "id_usuario": result[0],
                "cui": result[1],
                "nombre": result[2],
                "apellido": result[3],
                "correo": result[4],
                "telefono": result[5],
                "estado_sesion": result[6],
                "verificacion_correo": result[7],
                "created_at": result[8].strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": result[9].strftime("%Y-%m-%d %H:%M:%S")
            }

            return {
                "status": "success",
                "user": usuario
            }, 200  # OK

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        conn.close()


def actualizar_usuario(id_usuario, user):
    

    if not user:
        return {
            "status": "failed",
            "message": "No se enviaron datos para actualizar"
        }, 400  # Bad Request
    
    #Solo campos admitidos
    allowed_fields = ["cui", "nombre", "apellido", "correo", "telefono", "estado_sesion", "verificacion_correo"]

    for key in user.keys():
        if key not in allowed_fields:
            return {
                "status": "failed",
                "message": f"Campo no permitido: {key}"
            }, 400  # Bad Request


    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        
        #si intentan actualizar correo o cui verificar que no existan en la base de datos
        if "correo" in user:
            with conn.cursor() as cursor:
                cursor.execute(queriesUsuario["check_email_exists"], {"correo": user["correo"]})
                if cursor.fetchone()[0] > 0:
                    return {
                        "status": "failed",
                        "message": "El correo ya está en uso"
                    }, 409  # Conflict
                    
        if "cui" in user:
            with conn.cursor() as cursor:
                cursor.execute(queriesUsuario["check_cui_exists"], {"cui": user["cui"]})
                if cursor.fetchone()[0] > 0:
                    return {
                        "status": "failed",
                        "message": "El CUI ya está en uso"
                    }, 409
                

        with conn.cursor() as cursor:
            # Verificar si el usuario existe
            cursor.execute(queriesUsuario["get_user"], {"id_usuario": id_usuario})
            if cursor.fetchone() is None:
                return {
                    "status": "failed",
                    "message": f"Usuario con id {id_usuario} no encontrado"
                }, 404  # Not Found

            # Construir la consulta UPDATE dinámicamente
            set_clause = ", ".join([f"{key} = :{key}" for key in user.keys()])
            query = queriesUsuario["update_user"].format(set_clause=set_clause)
            
            # Agregar el ID del usuario a los parámetros
            user["id_usuario"] = id_usuario

            # Ejecutar la consulta
            cursor.execute(query, user)
            conn.commit()

            return {
                "status": "success",
                "message": "Usuario actualizado con éxito"
            }, 200  # OK

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        if conn:
            conn.close()

def eliminar_usuario(id_usuario):
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        
        with conn.cursor() as cursor:
            # Verificar si el usuario existe
            cursor.execute(queriesUsuario["get_user"], {"id_usuario": id_usuario})
            if cursor.fetchone() is None:
                return {
                    "status": "failed",
                    "message": f"Usuario con id {id_usuario} no encontrado"
                }, 404  # Not Found

            # Eliminar al usuario
            cursor.execute(queriesUsuario["delete_user"], {"id_usuario": id_usuario})
            conn.commit()

            return {
                "status": "success",
                "message": f"Usuario con id {id_usuario} eliminado con éxito"
            }, 200  # OK

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        if conn:
            conn.close()


               
def insertar_direccion(id_usuario, direccion):
    if not direccion:
        return {
            "status": "failed",
            "message": "No se enviaron datos para insertar"
        }, 400  # Bad Request
    
    if "direccion" not in direccion:
        return {
            "status": "failed",
            "message": "Falta el campo requerido: direccion"
        }, 400
    
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        
        #Verificar que el usuario con id_usuario exista con get_user, si hay respuesta insertar direccion

        

        with conn.cursor() as cursor:

            cursor.execute(queriesUsuario["get_user"], {"id_usuario": id_usuario})
            if cursor.fetchone() is None:
                return {
                    "status": "failed",
                    "message": f"Usuario con id {id_usuario} no encontrado"
                }, 404

            cursor.execute(queriesUsuario["insert_direccion"], {"id_usuario": id_usuario, "direccion": direccion["direccion"]})
            conn.commit()

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500
    
    finally:
        conn.close()

    return {
        "status": "success",
        "message": "Dirección insertada con éxito"
    }, 201  # Created


def insertar_metodo_pago(id_usuario, metodo_pago):
    if not metodo_pago:
        return {
            "status": "failed",
            "message": "No se enviaron datos para insertar"
        }, 400  # Bad Request
    
    if "metodo_pago" not in metodo_pago:
        return {
            "status": "failed",
            "message": "Falta el campo requerido: metodo_pago"
        }, 400
    
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        with conn.cursor() as cursor:

            cursor.execute(queriesUsuario["get_user"], {"id_usuario": id_usuario})
            if cursor.fetchone() is None:
                return {
                    "status": "failed",
                    "message": f"Usuario con id {id_usuario} no encontrado"
                }, 404

            cursor.execute(queriesUsuario["insert_metodo_pago"], {"id_usuario": id_usuario, "metodo_pago": metodo_pago["metodo_pago"]})
            conn.commit()

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500
    
    finally:
        conn.close()

    return {
        "status": "success",
        "message": "Método de pago insertado con éxito"
    }, 201  # Created

def obtener_direcciones(id_usuario):
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        with conn.cursor() as cursor:


            cursor.execute(queriesUsuario["get_direcciones"], {"id_usuario": id_usuario})
            direcciones = cursor.fetchall()


            if not direcciones:
                return {
                    "status": "failed",
                    "message": "No se encontraron direcciones"
                }, 404  # Not Found

            direcciones = [{"id_direccion": direccion[0], "direccion": direccion[1]} for direccion in direcciones]

            return {
                "status": "success",
                "direcciones": direcciones
            }, 200  # OK

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        conn.close()

def obtener_metodos_pago(id_usuario):
    try:
        conn = get_connection()
        if conn is None:
            return {
                "status": "failed",
                "message": "No se pudo conectar a la base de datos"
            }, 500  # Internal Server Error
        with conn.cursor() as cursor:
            cursor.execute(queriesUsuario["get_metodos_pago"], {"id_usuario": id_usuario})
            metodos_pago = cursor.fetchall()

            if not metodos_pago:
                return {
                    "status": "failed",
                    "message": "No se encontraron métodos de pago"
                }, 404  # Not Found

            metodos_pago = [{"id_metodo_pago": metodo_pago[0], "metodo_pago": metodo_pago[1]} for metodo_pago in metodos_pago]

            return {
                "status": "success",
                "metodos_pago": metodos_pago
            }, 200  # OK

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Ocurrió un error: {str(e)}"
        }, 500  # Internal Server Error

    finally:
        conn.close()


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))