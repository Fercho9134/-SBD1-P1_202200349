# queries.py

queries = {
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
    '''
}

