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

def actualizar_inventarios(cursor, id_producto, data, sedes):
    if "stock" in data:
        for stock in data["stock"]:
            if stock["sede"] not in sedes:
                return f"La sede con ID {stock['sede']} no existe", 400
            cursor.execute(queriesProducto["update_inventario"], {
                "id_producto": id_producto,
                "id_sede": stock["sede"],
                "stock": stock["stock"]
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


def obtener_productos(id=None):
    conn = get_connection()
    if conn is None:
        return {"status": "failed", "message": "No se pudo conectar a la base de datos"}, 500

    try:
        with conn.cursor() as cursor:
            if id:
                cursor.execute(queriesProducto["get_product_by_id"], {"id_producto": id})
            else:
                cursor.execute(queriesProducto["get_all_products"])
                
            productos_raw = cursor.fetchall()

            if id and not productos_raw:
                return {"status": "failed", "message": "Producto no encontrado"}, 404  # Producto no existe

            productos = {}

            for row in productos_raw:
                id_producto = row[0]

                if id_producto not in productos:
                    productos[id_producto] = {
                        "id_producto": id_producto,
                        "sku": row[1],
                        "nombre": row[2],
                        "descripcion": str(row[3].read()) if row[3] else "",  # Convertir CLOB a string
                        "precio": float(row[4]),  # Convertir a float
                        "slug": row[5],
                        "activo": row[6],
                        "categorias": [],
                        "imagenes": [],
                        "inventario": []
                    }

                # Agregar categorías sin duplicar
                id_categoria, nombre_categoria = row[7], row[8]
                if id_categoria and id_categoria not in [c["id_categoria"] for c in productos[id_producto]["categorias"]]:
                    productos[id_producto]["categorias"].append({"id_categoria": id_categoria, "nombre": nombre_categoria})

                # Agregar imágenes sin duplicar
                url_imagen = row[9]
                if url_imagen and url_imagen not in productos[id_producto]["imagenes"]:
                    productos[id_producto]["imagenes"].append(url_imagen)

                # Agregar stock por sede sin duplicar
                id_sede, nombre_sede, stock = row[10], row[11], row[12]
                if id_sede and id_sede not in [inv["id_sede"] for inv in productos[id_producto]["inventario"]]:
                    productos[id_producto]["inventario"].append({
                        "id_sede": id_sede,
                        "nombre_sede": nombre_sede,
                        "stock": stock
                    })

            if id:
                # Si solo se busca un producto por id, devolver solo ese producto, sin "productos"
                return {"status": "success", **productos[id_producto]}, 200
            else:
                # Si no se pasa id, devolver todos los productos dentro de "productos"
                return {"status": "success", "productos": list(productos.values())}, 200

    except Exception as e:
        return {"status": "failed", "message": f"Error al obtener productos: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def actualizar_produco(id_producto, data):
    #Unico campo requerido es el id_producto
    if not id_producto:
        return {"status": "failed", "message": "El campo id_producto es requerido"}, 400

    
    conn = None

    try:
        conn = get_connection()
        if conn is None:
            return {"status": "failed", "message": "No se pudo conectar a la base de datos"}, 500

        with conn.cursor() as cursor:

            # Verificar si el producto existe
            cursor.execute(queriesProducto["get_product_by_id"], {"id_producto": id_producto})
            producto = cursor.fetchone()
            if not producto:
                return {"status": "failed", "message": f"Producto con id {id_producto} no encontrado"}, 404

            # Verificar que los datos sean válidos, si el campo activo esta presente, verificar que sea TRUE o FALSE
            if "activo" in data:
                if data["activo"] not in ["TRUE", "FALSE"]:
                    return {"status": "failed", "message": "El campo activo debe ser 'TRUE' o 'FALSE'"}, 400
                
            #Si se encuentra el campo id_producto, indicar que no se puede actualizar el id
            if "id_producto" in data:
                return {"status": "failed", "message": "El campo id_producto no puede ser actualizado"}, 400
                
            #Si el sku esta presente, verificar que no exista en la base de datos
            if "sku" in data:
                cursor.execute(queriesProducto["get_product_by_sku"], {"sku": data["sku"]})
                sku_existente = cursor.fetchone()
                if sku_existente and sku_existente[0] != id_producto:  # No comparar con el propio producto
                    return {"status": "failed", "message": f"El SKU {data['sku']} ya está registrado en la base de datos"}, 400
                
                

            sedes = obtener_sedes(cursor)

            #Verificar inventarios
            error_message, status_code = verificar_inventarios(cursor, data, sedes)
            if error_message:
                return {"status": "failed", "message": error_message}, status_code
            
            #Verificar imagenes
            error_message, status_code = verificar_imagenes(data)
            if error_message:
                return {"status": "failed", "message": error_message}, status_code
            
            #Verificar categorias
            error_message, status_code = verificar_categorias(cursor, data)
            if error_message:
                return {"status": "failed", "message": error_message}, status_code
            


            #primero, si los campos stock, imagenes o categorias estan presentes, eliminarlos del diccionario. Pero guardarlos en variables
            stock = data.pop("stock", None)
            imagenes = data.pop("imagenes", None)
            categorias = data.pop("categorias", None)

            #update product se construira y ejecutara solo si los campos precio, sku etc estan presentes. Si no se cambiara informacion del producto no se ejecutara
            contador = 0
            required_fields = ["sku", "nombre", "descripcion", "precio", "slug", "activo"]
            for field in required_fields:
                if field not in data:
                    continue
                contador += 1

            if contador > 0:
                #Construir la clausula SET
                set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
                query = queriesProducto["update_product"].format(set_clause=set_clause)

                print("query", query)

                data["id_producto"] = id_producto
                
                cursor.execute(query, data)

            if stock:
                data["stock"] = stock
            if imagenes:
                data["imagenes"] = imagenes
            if categorias:
                data["categorias"] = categorias

            #Actualizar stock, imagenes y categorias

            #Borrar todas las imagenes y categorias asociadas al producto
            cursor.execute(queriesProducto["delete_images"], {"id_producto": id_producto})
            cursor.execute(queriesProducto["delete_categories"], {"id_producto": id_producto})

            #Insertar las nuevas imagenes y categorias
            if imagenes:
                print("entre a insertar imagenes")
                insertar_imagenes(cursor, id_producto, data)
                print("sali de insertar imagenes")
            if categorias:
                print("entre a insertar categorias")
                insertar_categorias(cursor, id_producto, data)
                print("sali de insertar categorias")

            #Actualizar stock
            if stock:
                print("entre a actualizar inventarios")
                actualizar_inventarios(cursor, id_producto, data, sedes)
                print("sali de actualizar inventarios")

            conn.commit()

            return {"status": "success", "message": f"Producto con id {id_producto} actualizado exitosamente"}, 200
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        if error.code == 1:
            return {"status": "failed", "message": f"Error de base de datos: {error.message}"}, 400
        return {"status": "failed", "message": f"Error de base de datos: {str(e)}"}, 500
    
    except Exception as e:

        return {"status": "failed", "message": f"Ocurrió un error inesperado: {str(e)}"}, 500
    
    finally:

        if conn:
            conn.close()




            
def borrarProducto(id_producto):
    conn = get_connection()
    if conn is None:
        return {"status": "failed", "message": "No se pudo conectar a la base de datos"}, 500

    try:
        with conn.cursor() as cursor:
            # Verificar si el producto existe
            cursor.execute(queriesProducto["get_product_by_id"], {"id_producto": id_producto})
            producto = cursor.fetchone()
            if not producto:
                return {"status": "failed", "message": f"Producto con id {id_producto} no encontrado"}, 404

            # Borrar el producto
            cursor.execute(queriesProducto["delete_product"], {"id_producto": id_producto})

            # Confirmar los cambios
            conn.commit()

            return {"status": "success", "message": f"Producto con id {id_producto} eliminado exitosamente"}, 200

    except Exception as e:
        return {"status": "failed", "message": f"Error al borrar producto: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
