CREATE TABLE usuarios (
    id_usuario NUMBER PRIMARY KEY,
    cui NUMBER(10) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    apellido VARCHAR2(100) NOT NULL,
    correo VARCHAR2(255) UNIQUE NOT NULL,
    telefono VARCHAR2(20),
    contrasena VARCHAR2(255) NOT NULL,
    estado_sesion VARCHAR2(20) CHECK (estado_sesion IN ('TRUE', 'FALSE')),
    verificacion_correo VARCHAR2(20) CHECK (verificacion_correo IN ('TRUE', 'FALSE')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE direcciones (
    id_direccion NUMBER PRIMARY KEY,
    id_usuario NUMBER NOT NULL,
    direccion VARCHAR2(255) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE metodos_de_pago (
    id_metodo NUMBER PRIMARY KEY,
    id_usuario NUMBER NOT NULL,
    metodo_pago VARCHAR2(100) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE trabajadores (
    id_trabajador NUMBER PRIMARY KEY,
    cui NUMBER(10) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    apellido VARCHAR2(100) NOT NULL,
    id_puesto NUMBER NOT NULL,
    id_sede NUMBER NOT NULL,
    id_departamento NUMBER NOT NULL,
    telefono VARCHAR2(20),
    correo_institucional VARCHAR2(255) UNIQUE NOT NULL,
    estado VARCHAR2(20) CHECK (estado IN ('TRUE', 'FALSE')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_puesto) REFERENCES puestos(id_puesto),
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede),
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

CREATE TABLE puestos (
    id_puesto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE sedes (
    id_sede NUMBER PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE departamentos (
    id_departamento NUMBER PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE productos (
    id_producto NUMBER PRIMARY KEY,
    sku VARCHAR2(50) UNIQUE NOT NULL,
    nombre VARCHAR2(255) NOT NULL,
    descripcion CLOB,
    precio NUMBER(12,2) NOT NULL,
    slug VARCHAR2(255) UNIQUE NOT NULL,
    activo CHAR(20) CHECK (activo IN ('TRUE', 'FALSE')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP 
  );

CREATE TABLE categorias (
    id_categoria NUMBER PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE producto_categoria (
    id_producto NUMBER NOT NULL,
    id_categoria NUMBER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_producto, id_categoria),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES
);

CREATE TABLE imagenes (
    id_imagen NUMBER PRIMARY KEY,
    id_producto NUMBER NOT NULL,
    url_imagen VARCHAR2(255) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

CREATE TABLE inventario_por_sede (
    id_inventario NUMBER PRIMARY KEY,
    id_producto NUMBER NOT NULL,
    id_sede NUMBER NOT NULL,
    stock NUMBER NOT NULL CHECK (stock >= 0),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede)
);

CREATE TABLE ordenes_de_compra(
    id_orden NUMBER PRIMARY KEY,
    id_usuario NUMBER,
    id_sede NUMBER NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede)
);

CREATE TABLE productos_orden (
    id_producto_orden NUMBER PRIMARY KEY,
    id_orden NUMBER NOT NULL,
    id_producto NUMBER NOT NULL,
    cantidad NUMBER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMBER NOT NULL CHECK (precio_unitario > 0),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE estados_pago (
    id_estado_pago NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE pagos (
    id_pago NUMBER PRIMARY KEY,
    id_orden NUMBER,
    metodo_pago VARCHAR2(100) NOT NULL,
    id_estado_pago NUMBER NOT NULL,
    monto_total NUMBER NOT NULL CHECK (monto_total > 0),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE SET NULL,
    FOREIGN KEY (id_estado_pago) REFERENCES estados_pago(id_estado_pago)
);

CREATE TABLE estado_envio (
    id_estado_envio NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE empresa_transporte (
    id_empresa NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE envios (
    id_envio NUMBER PRIMARY KEY,
    id_orden NUMBER,
    id_empresa NUMBER NOT NULL,
    direccion VARCHAR2(255) NOT NULL,
    guia_rastreo VARCHAR2(100) UNIQUE NOT NULL,
    id_estado_envio NUMBER NOT NULL,
    fecha_despacho TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE SET NULL,
    FOREIGN KEY (id_empresa) REFERENCES empresa_transporte(id_empresa),
    FOREIGN KEY (id_estado_envio) REFERENCES estado_envio(id_estado_envio)
);

CREATE TABLE estado_devolucion (
    id_estado_devolucion NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE devoluciones (
    id_devolucion NUMBER PRIMARY KEY,
    id_orden NUMBER,
    motivo CLOB NOT NULL,
    id_estado_devolucion NUMBER NOT NULL,
    fecha_solicitud TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE SET NULL,
    FOREIGN KEY (id_estado_devolucion) REFERENCES estado_devolucion(id_estado_devolucion)
);

CREATE TABLE estado_traslados(
    id_estado_traslado NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE traslados (
    id_traslado NUMBER PRIMARY KEY,
    id_sede_origen NUMBER NOT NULL,
    id_sede_destino NUMBER NOT NULL,
    id_estado_traslado NUMBER NOT NULL,
    fecha_movimiento TIMESTAMP,
    fecha_estimada_llagada TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_sede_origen) REFERENCES sedes(id_sede),
    FOREIGN KEY (id_sede_destino) REFERENCES sedes(id_sede),
    FOREIGN KEY (id_estado_traslado) REFERENCES estado_traslados(id_estado_traslado)
);

CREATE TABLE productos_traslado (
    id_producto_traslado NUMBER PRIMARY KEY,
    id_traslado NUMBER NOT NULL,
    id_producto NUMBER NOT NULL,
    cantidad NUMBER NOT NULL CHECK (cantidad > 0),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (id_traslado) REFERENCES traslados(id_traslado) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);


CREATE OR REPLACE TRIGGER calcular_monto_total
BEFORE INSERT ON pagos
FOR EACH ROW
DECLARE
    v_monto_total NUMBER;
BEGIN
    -- Calcula el monto total sumando (precio_unitario * cantidad) para todos los productos de la orden
    SELECT SUM(precio_unitario * cantidad)
    INTO v_monto_total
    FROM productos_orden
    WHERE id_orden = :NEW.id_orden;

    -- Asigna el monto total calculado al campo monto_total del nuevo registro
    :NEW.monto_total := NVL(v_monto_total, 0);  -- Si no hay productos, el monto total será 0
END;
/