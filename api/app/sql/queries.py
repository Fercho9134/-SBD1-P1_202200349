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
    '''
}

