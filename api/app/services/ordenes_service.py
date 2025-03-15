from app.sql.queries import queriesOrdenes, queriesUsuario
from app.db import get_connection
import cx_Oracle
import random
import time
import json
def insert_order(data):
    #Verificamos datos
    required_fields = ['id_usuario', 'id_sede', 'productos', 'id_direccion', 'id_metodo_pago']
    for field in required_fields:
        if field not in data:
            return {"status": "failed", "message": f"El campo {field} es requerido"}, 400
        
    #Abrimos conexión
    try:
        conn = get_connection()
        if conn is None:
            return {"error": "Error al conectar a la base de datos"}, 500
        
        with conn.cursor() as cursor:
            #Paso 1: verificaciones. Verificar que el usuario exista, que la sede exista, que los productos existan y que haya stock

            #Verificar que el usuario, direccion y metodo de pago existan
            cursor.execute(queriesUsuario['get_user'], id_usuario=data['id_usuario'])
            if cursor.fetchone() is None:
                return {"status": "failed", "message": f"El usuario con id {data['id_usuario']} no existe"}, 404

            #Verificar que la sede exista             
            cursor.execute(queriesOrdenes['getSedes'], id_sede=data['id_sede'])
            if cursor.fetchone() is None:
                return {"status": "failed", "message": f"La sede con id {data['id_sede']} no existe"}, 404
            
            #Verificar que la direccion exista
            cursor.execute(queriesOrdenes['get_direccion_by_id'], id_direccion=data['id_direccion'])
            if cursor.fetchone() is None:
                return {"status": "failed", "message": f"La direccion con id {data['id_direccion']} no existe"}, 404
            
            #Verificar que el metodo de pago exista
            cursor.execute(queriesOrdenes['get_metodo_pago_by_id'], id_metodo=data['id_metodo_pago'])
            if cursor.fetchone() is None:
                return {"status": "failed", "message": f"El metodo de pago con id {data['id_metodo_pago']} no existe"}, 404
            
            #Verificar que los productos existan y que haya stock
            #La estructura de cada producto es {"id_producto": 1, "cantidad": 2}
            print("Entro a verificar productos")

            #Si productos esta vacio
            if len(data['productos']) == 0:
                return {"status": "failed", "message": "La orden debe tener al menos un producto"}, 400

            for producto in data['productos']:

                #Verificar que cantidad sea un entero positivo
                if not isinstance(producto['cantidad'], int) or producto['cantidad'] <= 0:
                    return {"status": "failed", "message": f"La cantidad del producto con id {producto['id_producto']} debe ser un entero positivo"}, 400

                cursor.execute(queriesOrdenes['verificar_stock'], id_producto=producto['id_producto'], id_sede=data['id_sede'])
                stock = cursor.fetchone()


                if stock is None:
                    return {
                        "status": "failed",
                        "message": f"El producto con id {producto['id_producto']} no existe"
                    }, 404

                # Si el stock es None, lo tomamos como 0
                stock_actual = stock[0] if stock[0] is not None else 0

                if stock_actual < producto['cantidad']:
                    return {
                        "status": "failed",
                        "message": f"No hay suficiente stock del producto con id {producto['id_producto']}. "
                                f"Únicamente hay {stock_actual} unidades disponibles en la sede con id {data['id_sede']}"
                    }, 400

                # Si todo está bien, actualizar el stock
                cursor.execute(
                    queriesOrdenes['actualizar_stock'],
                    {"stock": stock_actual - producto['cantidad'], "id_producto": producto['id_producto'], "id_sede": data['id_sede']}
                )

            print("Paso las verificaciones")

                
            #Paso 2: Insertar la orden

            id_orden = cursor.var(int)
            cursor.execute(queriesOrdenes['insert_order'], {"id_usuario": data['id_usuario'], "id_sede": data['id_sede'], "id_orden": id_orden})
            print("Paso el insert de la orden")

            id_orden = id_orden.getvalue()[0]

            #Paso 3: Insertar los detalles de la orden
            for producto in data['productos']:
                cursor.execute(queriesOrdenes['insert_order_detail'], {"id_orden": id_orden, "id_producto": producto['id_producto'], "cantidad": producto['cantidad']})
                
            print("Paso el insert de los detalles")

            #Paso 4: Generar el envio
            guia = generar_guia_rastreo()

            #obtenemos las ids de las empresas disponibles
            cursor.execute(queriesOrdenes['get_empresas_envio'])
            empresas = cursor.fetchall()

            #empresas envio nos devuelve una lista con las ids de las empresas de envio
            #Seleccionamos una empresa aleatoria
            id_empresa = random.choice(empresas)[0]

            #La id del envio esta en data
            #En fecha_despacho la fecha actual

            cursor.execute(queriesOrdenes['insert_envio'], {"id_orden": id_orden, "id_empresa": id_empresa, "id_direccion_envio": data['id_direccion'], "guia_rastreo": guia, "id_estado_envio": 1, "fecha_despacho": cx_Oracle.TimestampFromTicks(time.time())})

            #Paso 5: Insertar pago
            cursor.execute(queriesOrdenes['insert_pago'], {"id_orden": id_orden, "id_metodo_pago": data['id_metodo_pago'], "id_estado_pago": 1})

            conn.commit()
            return {"status": "success", "message": "Se creo la orden exitosamente con la id {}".format(id_orden)}, 201
    except cx_Oracle.Error as e:
        return {"status": "failed", "message": f"Error al insertar la orden: {e}"}, 500
    finally:
        conn.close()

def get_all_orders():
    try:
        conn = get_connection()
        if conn is None:
            return {"error": "Error al conectar a la base de datos"}, 500
        
        with conn.cursor() as cursor:
            cursor.execute(queriesOrdenes['get_all_orders'])

            # Obtener los nombres de las columnas para formatear los resultados
            column_names = [col[0].lower() for col in cursor.description]
            
            # Convertir los resultados en una lista de diccionarios
            orders = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            
            # Estructurar los datos en un formato más legible
            formatted_orders = []
            for order in orders:
                formatted_orders.append({
                    "ID Orden": order["id_orden"],
                    "Usuario": {
                        "ID": order["id_usuario"],
                        "Nombre": f"{order['nombre_usuario']} {order['apellido_usuario']}"
                    },
                    "Sede": {
                        "ID": order["id_sede"],
                        "Nombre": order["nombre_sede"]
                    },
                    "Fecha de Compra": order["fecha_compra"],
                    "Envío": {
                        "ID Envío": order["id_envio"],
                        "Empresa de Transporte": order["nombre_empresa"],
                        "Dirección de Envío": order["direccion_envio"],
                        "Guía de Rastreo": order["guia_rastreo"],
                        "Estado de Envío": order["nombre_estado_envio"]
                    },
                    "Pago": {
                        "ID Pago": order["id_pago"],
                        "Método de Pago": order["nombre_metodo_pago"],
                        "Estado de Pago": order["nombre_estado_pago"],
                        "Monto_total": order["monto_total"]
                    }
                })

            return {"status": "success", "orders": formatted_orders}, 200

    except cx_Oracle.Error as e:
        return {"status": "failed", "message": f"Error al obtener las órdenes: {e}"}, 500

    finally:
        if conn:
            conn.close()

def get_order_by_id(order_id):
    try:
        conn = get_connection()
        if conn is None:
            return {"error": "Error al conectar a la base de datos"}, 500
        
        with conn.cursor() as cursor:
            cursor.execute(queriesOrdenes['get_order_by_id'], {"id_orden": order_id})
            order = cursor.fetchone()
            
            if order is None:
                return {"status": "failed", "message": "Orden no encontrada"}, 404

            # Obtener nombres de columnas
            column_names = [col[0].lower() for col in cursor.description]

            # Convertir a diccionario
            order_data = dict(zip(column_names, order))

            # Convertir productos de JSON a lista de diccionarios
            order_data["productos"] = json.loads(order_data["productos"]) if order_data["productos"] else []

            # Estructurar los datos
            formatted_order = {
                "ID Orden": order_data["id_orden"],
                "Usuario": {
                    "ID": order_data["id_usuario"],
                    "Nombre": f"{order_data['nombre_usuario']} {order_data['apellido_usuario']}"
                },
                "Sede": {
                    "ID": order_data["id_sede"],
                    "Nombre": order_data["nombre_sede"]
                },
                "Fecha de Compra": order_data["fecha_compra"],
                "Envío": {
                    "ID Envío": order_data["id_envio"],
                    "Empresa de Transporte": order_data["nombre_empresa"],
                    "Dirección de Envío": order_data["direccion_envio"],
                    "Guía de Rastreo": order_data["guia_rastreo"],
                    "Estado de Envío": order_data["nombre_estado_envio"]
                },
                "Pago": {
                    "ID Pago": order_data["id_pago"],
                    "Método de Pago": order_data["nombre_metodo_pago"],
                    "Estado de Pago": order_data["nombre_estado_pago"],
                    "Monto Total": order_data["monto_total"]
                },
                "Productos": order_data["productos"]
            }

            return {"status": "success", "order": formatted_order}, 200

    except cx_Oracle.Error as e:
        return {"status": "failed", "message": f"Error al obtener la orden: {e}"}, 500

    finally:
        if conn:
            conn.close()




        

def generar_guia_rastreo():
    #Generara una guia de rastreo aleatoria alfanumerica de 10 caracteres
    #formato LLL-NNNNNN
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numeros = "0123456789"
    guia = ""
    for i in range(3):
        guia += random.choice(letras)
    guia += "-"
    for i in range(6):
        guia += random.choice(numeros)
    return guia

            