from app.sql.queries import queriesProducto
from app.db import get_connection
import cx_Oracle

def verificar_sku_existente(cursor, sku):
    cursor.execute(queriesProducto['get_producto_by_sku'], {"sku": sku})
    resultado = cursor.fetchone()
    return resultado is not None and resultado[0] > 0

def obtener_sedes(cursor):
    cursor.execute(queriesProducto['get_sedes'])
    return [s[0] for s in cursor.fetchall()]

def validar_categoria(cursor, categoria_id):
    cursor.execute(queriesProducto['get_categoria'], {"id_categoria": categoria_id})
    resultado = cursor.fetchone()
    return resultado is not None and resultado[0] > 0

def verificar_datos(data):
    # Verificar que todos los campos requeridos estén presentes
    campos_requeridos = ["sku", "nombre", "descripcion", "precio", "slug"]
    for campo in campos_requeridos:
        if campo not in data:
            return f"El campo {campo} es requerido", 400

    # Verificar que el precio sea un número positivo
    if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
        return "El precio debe ser un número positivo", 400

    # Si "activo" no está presente, asignarlo a "TRUE"
    if "activo" not in data:
        data["activo"] = "TRUE"

    # Verificar que el campo "activo" sea "TRUE" o "FALSE"
    if data["activo"] not in ["TRUE", "FALSE"]:
        return "El campo activo debe ser 'TRUE' o 'FALSE'", 400

    return None, None

def verificar_inventarios(cursor, data, sedes):
    # Verificar que los inventarios sean válidos
    if "stock" in data:
        for stock in data["stock"]:
            if stock["sede"] not in sedes:
                return f"La sede con ID {stock['sede']} no existe", 400
    return None, None

def verificar_imagenes(data):
    # Verificar que las imágenes sean válidas
    if "imagenes" in data:
        if not isinstance(data["imagenes"], list) or len(data["imagenes"]) == 0:
            return "Las imágenes deben ser una lista no vacía", 400
    return None, None

def verificar_categorias(cursor, data):
    # Verificar que las categorías sean válidas
    if "categorias" in data:
        for categoria in data["categorias"]:
            if not validar_categoria(cursor, categoria):
                return f"La categoría con ID {categoria} no existe", 400
    return None, None

def insertar_producto(cursor, data):
    # Definimos el parámetro de salida para capturar el id_producto
    id_producto = cursor.var(int)  # Creamos una variable de salida de tipo entero

    # Ejecutamos la consulta SQL
    cursor.execute(queriesProducto["insert_product"], {
        "sku": data["sku"],
        "nombre": data["nombre"],
        "descripcion": data["descripcion"],
        "precio": data["precio"],
        "slug": data["slug"],
        "activo": data["activo"],
        "id_producto": id_producto  # Pasamos la variable de salida
    })

    # Obtenemos el valor de id_producto desde la variable de salida
    return id_producto.getvalue()[0]

def insertar_inventarios(cursor, id_producto, data, sedes):
    if "stock" in data:
        for stock in data["stock"]:
            if stock["sede"] not in sedes:
                return f"La sede con ID {stock['sede']} no existe", 400
            cursor.execute(queriesProducto["insert_inventario"], {
                "id_producto": id_producto,
                "id_sede": stock["sede"],
                "stock": stock["stock"]
            })

        sedes_ids = set(sedes)
        especificadas_ids = set(stock["sede"] for stock in data["stock"])
        for sede_id in sedes_ids - especificadas_ids:
            cursor.execute(queriesProducto["insert_inventario"], {
                "id_producto": id_producto,
                "id_sede": sede_id,
                "stock": None
            })
    else:
        for sede_id in sedes:
            cursor.execute(queriesProducto["insert_inventario"], {
                "id_producto": id_producto,
                "id_sede": sede_id,
                "stock": None
            })

def insertar_imagenes(cursor, id_producto, imagenes):
    if "imagenes" in imagenes:
        for imagen in imagenes["imagenes"]:
            cursor.execute(queriesProducto["insert_imagen"], {
                "id_producto": id_producto,
                "url_imagen": imagen
            })

def insertar_categorias(cursor, id_producto, categorias):
    if "categorias" in categorias:
        for categoria in categorias["categorias"]:
            cursor.execute(queriesProducto["insert_categoria"], {
                "id_producto": id_producto,
                "id_categoria": categoria
            })

def crear_producto(data):
    # Verificación de datos antes de cualquier inserción
    error_message, status_code = verificar_datos(data)
    if error_message:
        return {"status": "failed", "message": error_message}, status_code
    
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return {"status": "failed", "message": "No se pudo conectar a la base de datos"}, 500

        with conn.cursor() as cursor:
            # Verificar si el SKU ya existe
            if verificar_sku_existente(cursor, data["sku"]):
                return {"status": "failed", "message": f"El SKU {data['sku']} ya está registrado en la base de datos"}, 400

            # Obtener las sedes disponibles
            sedes = obtener_sedes(cursor)

            # Verificar inventarios
            error_message, status_code = verificar_inventarios(cursor, data, sedes)
            if error_message:
                return {"status": "failed", "message": error_message}, status_code

            # Verificar imágenes
            error_message, status_code = verificar_imagenes(data)
            if error_message:
                return {"status": "failed", "message": error_message}, status_code

            # Verificar categorías
            error_message, status_code = verificar_categorias(cursor, data)
            if error_message:
                return {"status": "failed", "message": error_message}, status_code

            # Insertar el producto

            id_producto = insertar_producto(cursor, data)

            # Insertar inventarios, imágenes y categorías
            insertar_inventarios(cursor, id_producto, data, sedes)
            insertar_imagenes(cursor, id_producto, data)
            insertar_categorias(cursor, id_producto, data)

            # Confirmar los cambios
            conn.commit()

            return {"status": "success", "message": f"Producto {data['nombre']} creado exitosamente con el id {id_producto}"}, 201
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        if error.code == 1:  # Violación de restricción UNIQUE (por ejemplo, SKU duplicado)
            return {"status": "failed", "message": f"Error de base de datos: {error.message}"}, 400
        return {"status": "failed", "message": f"Error de base de datos: {str(e)}"}, 500

    except Exception as e:
        return {"status": "failed", "message": f"Ocurrió un error inesperado: {str(e)}"}, 500

    finally:
        if conn:
            conn.close()
