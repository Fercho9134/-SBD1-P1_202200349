# queries.py

queriesUsuario = {
    'insert_user': '''
        INSERT INTO usuarios (
            cui, nombre, apellido, correo, telefono, contrasena, 
            estado_sesion, verificacion_correo
        ) 
        VALUES (
            :cui, :nombre, :apellido, :correo, :telefono, :contrasena, 
            :estado_sesion, :verificacion_correo
        )
    ''',

    'check_email_exists': '''
        SELECT COUNT(*) FROM usuarios WHERE correo = :correo
    ''',

    'check_cui_exists': '''
        SELECT COUNT(*) FROM usuarios WHERE cui = :cui
    ''',

    'get_password': '''
        SELECT id_usuario, contrasena FROM usuarios WHERE correo = :correo
    ''',

    'get_user': '''
        SELECT id_usuario, cui, nombre, apellido, correo, telefono, estado_sesion, verificacion_correo, created_at, updated_at FROM usuarios WHERE id_usuario = :id_usuario
    ''',

    'update_user': '''
        UPDATE usuarios SET {set_clause} WHERE id_usuario = :id_usuario
    ''',

    'delete_user': '''
        DELETE FROM usuarios WHERE id_usuario = :id_usuario
    ''',

    "insert_direccion": '''
        INSERT INTO direcciones (id_usuario, direccion)
        VALUES (:id_usuario, :direccion)
    ''',
    "insert_metodo_pago": '''
        INSERT INTO metodos_de_pago (id_usuario, metodo_pago)
        VALUES (:id_usuario, :metodo_pago)
    ''',
    "get_direcciones": '''
        SELECT id_direccion, direccion FROM direcciones WHERE id_usuario = :id_usuario
    ''',
    "get_metodos_pago": '''
        SELECT id_metodo, metodo_pago FROM metodos_de_pago WHERE id_usuario = :id_usuario
    '''
}

queriesProducto = {
    'insert_product': '''
        INSERT INTO productos (
            sku, nombre, descripcion, precio, slug, activo
        ) 
        VALUES (
            :sku, :nombre, :descripcion, :precio, :slug, :activo
        )
        RETURNING id_producto into :id_producto
    ''',

    'insert_inventario': '''
        INSERT INTO inventario_por_sede (id_producto, id_sede, stock)
        VALUES (:id_producto, :id_sede, :stock)
    ''',

    'insert_imagen': '''
        INSERT INTO imagenes (id_producto, url_imagen)
        VALUES (:id_producto, :url_imagen)
    ''',

    'insert_categoria': '''
        INSERT INTO producto_categoria (id_producto, id_categoria)
        VALUES (:id_producto, :id_categoria)
    ''',

    'get_sedes': '''SELECT id_sede FROM sedes''',

    'get_categoria': '''
        SELECT COUNT(*) FROM categorias WHERE id_categoria = :id_categoria
    ''',

    'get_producto_by_sku': '''
        SELECT COUNT(*) FROM productos WHERE sku = :sku
    ''',
    'get_product_by_sku': '''
        SELECT id_producto FROM productos WHERE sku = :sku
    ''',

    "get_all_products": """
        SELECT 
            p.id_producto,
            p.sku,
            p.nombre AS nombre_producto,
            p.descripcion,
            p.precio,
            p.slug,
            p.activo,

            -- Categorías (pueden no tener)
            c.id_categoria,
            c.nombre AS nombre_categoria,

            -- Imágenes (pueden no tener)
            i.url_imagen,

            -- Stock por sede (pueden no tener)
            s.id_sede,
            s.nombre AS nombre_sede,
            inv.stock

        FROM productos p
        LEFT JOIN producto_categoria pc ON p.id_producto = pc.id_producto
        LEFT JOIN categorias c ON pc.id_categoria = c.id_categoria
        LEFT JOIN imagenes i ON p.id_producto = i.id_producto
        LEFT JOIN inventario_por_sede inv ON p.id_producto = inv.id_producto
        LEFT JOIN sedes s ON inv.id_sede = s.id_sede
        ORDER BY p.id_producto
    """,

    "get_product_by_id": """
        SELECT 
            p.id_producto,
            p.sku,
            p.nombre AS nombre_producto,
            p.descripcion,
            p.precio,
            p.slug,
            p.activo,

            -- Categorías (pueden no tener)
            c.id_categoria,
            c.nombre AS nombre_categoria,

            -- Imágenes (pueden no tener)
            i.url_imagen,

            -- Stock por sede (pueden no tener)
            s.id_sede,
            s.nombre AS nombre_sede,
            inv.stock

        FROM productos p
        LEFT JOIN producto_categoria pc ON p.id_producto = pc.id_producto
        LEFT JOIN categorias c ON pc.id_categoria = c.id_categoria
        LEFT JOIN imagenes i ON p.id_producto = i.id_producto
        LEFT JOIN inventario_por_sede inv ON p.id_producto = inv.id_producto
        LEFT JOIN sedes s ON inv.id_sede = s.id_sede
        WHERE p.id_producto = :id_producto
    """,

    'update_product': '''
        UPDATE productos SET {set_clause} WHERE id_producto = :id_producto
    ''',

    'delete_images': '''
        DELETE FROM imagenes WHERE id_producto = :id_producto
    ''',

    'delete_categories': '''
        DELETE FROM producto_categoria WHERE id_producto = :id_producto
    ''',

    'update_inventario': '''
        UPDATE inventario_por_sede SET stock = :stock WHERE id_producto = :id_producto AND id_sede = :id_sede
    ''',

    'delete_product': '''
        DELETE FROM productos WHERE id_producto = :id_producto
    ''',
}


queriesOrdenes = {
    'insert_order': '''
        INSERT INTO ordenes_de_compra (
            id_usuario, id_sede)
            VALUES (:id_usuario, :id_sede)
            RETURNING id_orden into :id_orden
            ''',

    'insert_order_detail': '''
    INSERT INTO productos_orden (
        id_orden, id_producto, cantidad, precio_unitario
    )
        VALUES (
            :id_orden, 
            :id_producto, 
            :cantidad, 
            (SELECT precio FROM productos WHERE id_producto = :id_producto)
        )
        ''',
    
    "verificar_stock": '''
        SELECT stock FROM inventario_por_sede WHERE id_producto = :id_producto AND id_sede = :id_sede
    ''',

    "actualizar_stock": '''
        UPDATE inventario_por_sede SET stock = :stock WHERE id_producto = :id_producto AND id_sede = :id_sede
    ''',

    "getSedes": '''
        SELECT id_sede FROM sedes where id_sede = :id_sede
    ''',

    "getProductos": '''
        SELECT id_producto FROM productos
    ''',
    "insert_envio": '''
        INSERT INTO envios (id_orden, id_empresa, id_direccion_envio, guia_rastreo, id_estado_envio, fecha_despacho)
        VALUES (:id_orden, :id_empresa, :id_direccion_envio, :guia_rastreo, :id_estado_envio, :fecha_despacho)
    ''',
    "get_empresas_envio": '''
        SELECT id_empresa FROM empresa_transporte
    ''',
    "insert_pago": '''
        INSERT INTO pagos (id_orden, id_metodo_pago, id_estado_pago)
        VALUES (:id_orden, :id_metodo_pago, :id_estado_pago)
    ''',

    "get_direccion_by_id": '''
        SELECT direccion FROM direcciones WHERE id_direccion = :id_direccion
    ''',

    "get_metodo_pago_by_id": '''
        SELECT metodo_pago FROM metodos_de_pago WHERE id_metodo = :id_metodo
    ''',
    "get_orderes": '''
        SELECT id_orden, id_usuario, id_sede, fecha_compra FROM ordenes_de_compra
    ''',
    "get_envios": '''
        SELECT id_envio, id_orden, id_empresa, id_direccion_envio, guia_rastreo, id_estado_envio, fecha_despacho FROM envios
    ''',

    "get_all_orders": """
        SELECT

        oc.id_orden,
        oc.id_usuario,
        u.nombre AS nombre_usuario,
        u.apellido AS apellido_usuario,
        oc.id_sede,
        s.nombre AS nombre_sede,
        oc.created_at AS fecha_compra,

        --- Informacion envio
        e.id_envio,
        e.id_empresa,
        et.nombre AS nombre_empresa,
        e.id_direccion_envio,
        d.direccion AS direccion_envio,
        e.guia_rastreo,
        e.id_estado_envio,
        ee.nombre AS nombre_estado_envio,
        
        --- Informacion de pago
        p.id_pago,
        p.id_metodo_pago,
        mp.metodo_pago AS nombre_metodo_pago,
        p.id_estado_pago,
        ep.nombre AS nombre_estado_pago,
        p.monto_total

        FROM ordenes_de_compra oc
        LEFT JOIN usuarios u ON oc.id_usuario = u.id_usuario
        LEFT JOIN sedes s ON oc.id_sede = s.id_sede
        LEFT JOIN envios e ON oc.id_orden = e.id_orden
        LEFT JOIN empresa_transporte et ON e.id_empresa = et.id_empresa
        LEFT JOIN direcciones d ON e.id_direccion_envio = d.id_direccion
        LEFT JOIN estado_envio ee ON e.id_estado_envio = ee.id_estado_envio
        LEFT JOIN pagos p ON oc.id_orden = p.id_orden
        LEFT JOIN metodos_de_pago mp ON p.id_metodo_pago = mp.id_metodo
        LEFT JOIN estados_pago ep ON p.id_estado_pago = ep.id_estado_pago

        ORDER BY oc.id_orden
    """,

    #query para obtener una orden de pago en especifico, junto a sus productos, productos debe de tener id_producto, nombre_producto, cantidad. todo en un solo query
    "get_order_by_id": """
        SELECT
            oc.id_orden,
            oc.id_usuario,
            u.nombre AS nombre_usuario,
            u.apellido AS apellido_usuario,
            oc.id_sede,
            s.nombre AS nombre_sede,
            oc.created_at AS fecha_compra,

            -- Información de envío
            e.id_envio,
            et.nombre AS nombre_empresa,
            d.direccion AS direccion_envio,
            e.guia_rastreo,
            ee.nombre AS nombre_estado_envio,

            -- Información de pago
            p.id_pago,
            mp.metodo_pago AS nombre_metodo_pago,
            ep.nombre AS nombre_estado_pago,
            p.monto_total,

            -- Productos de la orden
            (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'id_producto' VALUE po.id_producto,
                        'nombre_producto' VALUE p.nombre,
                        'cantidad' VALUE po.cantidad
                    )
                )
                FROM productos_orden po
                LEFT JOIN productos p ON po.id_producto = p.id_producto
                WHERE po.id_orden = oc.id_orden
            ) AS productos

        FROM ordenes_de_compra oc
        LEFT JOIN usuarios u ON oc.id_usuario = u.id_usuario
        LEFT JOIN sedes s ON oc.id_sede = s.id_sede
        LEFT JOIN envios e ON oc.id_orden = e.id_orden
        LEFT JOIN empresa_transporte et ON e.id_empresa = et.id_empresa
        LEFT JOIN direcciones d ON e.id_direccion_envio = d.id_direccion
        LEFT JOIN estado_envio ee ON e.id_estado_envio = ee.id_estado_envio
        LEFT JOIN pagos p ON oc.id_orden = p.id_orden
        LEFT JOIN metodos_de_pago mp ON p.id_metodo_pago = mp.id_metodo
        LEFT JOIN estados_pago ep ON p.id_estado_pago = ep.id_estado_pago

        WHERE oc.id_orden = :id_orden
    """
    
}