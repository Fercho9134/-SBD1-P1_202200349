-- Eliminamos todas las tablas si existen
-- Eliminamos todas las tablas si existen
DROP TABLE usuarios CASCADE CONSTRAINTS;
DROP TABLE direcciones CASCADE CONSTRAINTS;
DROP TABLE metodos_de_pago CASCADE CONSTRAINTS;
DROP TABLE trabajadores CASCADE CONSTRAINTS;
DROP TABLE puestos CASCADE CONSTRAINTS;
DROP TABLE sedes CASCADE CONSTRAINTS;
DROP TABLE departamentos CASCADE CONSTRAINTS;
DROP TABLE productos CASCADE CONSTRAINTS;
DROP TABLE categorias CASCADE CONSTRAINTS;
DROP TABLE producto_categoria CASCADE CONSTRAINTS;
DROP TABLE imagenes CASCADE CONSTRAINTS;
DROP TABLE inventario_por_sede CASCADE CONSTRAINTS;
DROP TABLE ordenes_de_compra CASCADE CONSTRAINTS;
DROP TABLE productos_orden CASCADE CONSTRAINTS;
DROP TABLE estados_pago CASCADE CONSTRAINTS;
DROP TABLE pagos CASCADE CONSTRAINTS;
DROP TABLE estado_envio CASCADE CONSTRAINTS;
DROP TABLE empresa_transporte CASCADE CONSTRAINTS;
DROP TABLE envios CASCADE CONSTRAINTS;
DROP TABLE estado_devolucion CASCADE CONSTRAINTS;
DROP TABLE devoluciones CASCADE CONSTRAINTS;
DROP TABLE estado_traslados CASCADE CONSTRAINTS;
DROP TABLE traslados CASCADE CONSTRAINTS;
DROP TABLE productos_traslado CASCADE CONSTRAINTS;

CREATE TABLE usuarios (
    id_usuario NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cui NUMBER(10) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    apellido VARCHAR2(100) NOT NULL,
    correo VARCHAR2(255) UNIQUE NOT NULL,
    telefono VARCHAR2(20) NOT NULL,
    contrasena VARCHAR2(255) NOT NULL,
    estado_sesion VARCHAR2(20) NOT NULL CHECK (estado_sesion IN ('TRUE', 'FALSE')),
    verificacion_correo VARCHAR2(20) NOT NULL CHECK (verificacion_correo IN ('TRUE', 'FALSE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE direcciones (
    id_direccion NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario NUMBER NOT NULL,
    direccion VARCHAR2(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE metodos_de_pago (
    id_metodo NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario NUMBER NOT NULL,
    metodo_pago VARCHAR2(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE puestos (
    id_puesto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE sedes (
    id_sede NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE departamentos (
    id_departamento NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE trabajadores (
    id_trabajador NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cui NUMBER(10) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    apellido VARCHAR2(100) NOT NULL,
    id_puesto NUMBER NOT NULL,
    id_sede NUMBER NOT NULL,
    id_departamento NUMBER NOT NULL,
    telefono VARCHAR2(20) NOT NULL,
    correo_institucional VARCHAR2(255) UNIQUE NOT NULL,
    estado VARCHAR2(20) NOT NULL CHECK (estado IN ('TRUE', 'FALSE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_puesto) REFERENCES puestos(id_puesto),
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede),
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

CREATE TABLE productos (
    id_producto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku VARCHAR2(50) UNIQUE NOT NULL,
    nombre VARCHAR2(255) NOT NULL,
    descripcion CLOB NOT NULL,
    precio NUMBER(12,2) NOT NULL,
    slug VARCHAR2(255) UNIQUE NOT NULL,
    activo CHAR(20) NOT NULL CHECK (activo IN ('TRUE', 'FALSE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
  );

CREATE TABLE categorias (
    id_categoria NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE producto_categoria (
    id_producto NUMBER NOT NULL,
    id_categoria NUMBER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id_producto, id_categoria),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE CASCADE
);

CREATE TABLE imagenes (
    id_imagen NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_producto NUMBER NOT NULL,
    url_imagen VARCHAR2(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

CREATE TABLE inventario_por_sede (
    id_inventario NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_producto NUMBER NOT NULL,
    id_sede NUMBER NOT NULL,
    stock NUMBER CHECK (stock >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede)
);

CREATE TABLE ordenes_de_compra(
    id_orden NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario NUMBER,
    id_sede NUMBER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_sede) REFERENCES sedes(id_sede)
);

CREATE TABLE productos_orden (
    id_producto_orden NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_orden NUMBER NOT NULL,
    id_producto NUMBER NOT NULL,
    cantidad NUMBER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMBER NOT NULL CHECK (precio_unitario > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE estados_pago (
    id_estado_pago NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE pagos (
    id_pago NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_orden NUMBER ,
    id_metodo_pago NUMBER NOT NULL,
    id_estado_pago NUMBER NOT NULL,
    monto_total NUMBER NOT NULL CHECK (monto_total > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE SET NULL,
    FOREIGN KEY (id_estado_pago) REFERENCES estados_pago(id_estado_pago),
    FOREIGN KEY (id_metodo_pago) REFERENCES metodos_de_pago(id_metodo)
);

CREATE TABLE estado_envio (
    id_estado_envio NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE empresa_transporte (
    id_empresa NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE envios (
    id_envio NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_orden NUMBER,
    id_empresa NUMBER NOT NULL,
    id_direccion_envio NUMBER NOT NULL,
    guia_rastreo VARCHAR2(100) UNIQUE NOT NULL,
    id_estado_envio NUMBER NOT NULL,
    fecha_despacho TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE SET NULL,
    FOREIGN KEY (id_empresa) REFERENCES empresa_transporte(id_empresa),
    FOREIGN KEY (id_direccion_envio) REFERENCES direcciones(id_direccion),
    FOREIGN KEY (id_estado_envio) REFERENCES estado_envio(id_estado_envio)
);

CREATE TABLE estado_devolucion (
    id_estado_devolucion NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE devoluciones (
    id_devolucion NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_orden NUMBER,
    motivo CLOB NOT NULL,
    id_estado_devolucion NUMBER NOT NULL,
    fecha_solicitud TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_orden) REFERENCES ordenes_de_compra(id_orden) ON DELETE SET NULL,
    FOREIGN KEY (id_estado_devolucion) REFERENCES estado_devolucion(id_estado_devolucion)
);

CREATE TABLE estado_traslados(
    id_estado_traslado NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE traslados (
    id_traslado NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_sede_origen NUMBER NOT NULL,
    id_sede_destino NUMBER NOT NULL,
    id_estado_traslado NUMBER NOT NULL,
    fecha_movimiento TIMESTAMP NOT NULL,
    fecha_estimada_llegada TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_sede_origen) REFERENCES sedes(id_sede),
    FOREIGN KEY (id_sede_destino) REFERENCES sedes(id_sede),
    FOREIGN KEY (id_estado_traslado) REFERENCES estado_traslados(id_estado_traslado)
);

CREATE TABLE productos_traslado (
    id_producto_traslado NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_traslado NUMBER NOT NULL,
    id_producto NUMBER NOT NULL,
    cantidad NUMBER NOT NULL CHECK (cantidad > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
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


BEGIN
    FOR rec IN (SELECT table_name
                FROM all_tab_columns
                WHERE column_name = 'UPDATED_AT'
                  AND owner = 'TIENDA') -- Cambia el esquema si es necesario
    LOOP
        EXECUTE IMMEDIATE 'CREATE OR REPLACE TRIGGER trg_update_' || rec.table_name || '
                           BEFORE UPDATE ON ' || rec.table_name || '
                           FOR EACH ROW
                           BEGIN
                               :NEW.updated_at := CURRENT_TIMESTAMP;
                           END;';
    END LOOP;
END;
/


-- Insertamos los datos fijos, como sede, departamentos, puestos, etc. !0 de cada uno
INSERT INTO sedes (nombre) VALUES ('Sede Central');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 1');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 2');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 3');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 4');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 5');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 6');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 7');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 8');
INSERT INTO sedes (nombre) VALUES ('Sede Zona 9');

INSERT INTO departamentos (nombre) VALUES ('Departamento de Ventas');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Compras');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Recursos Humanos');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Logística');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Sistemas');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Contabilidad');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Marketing');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Atención al Cliente');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Almacén');
INSERT INTO departamentos (nombre) VALUES ('Departamento de Producción');

INSERT INTO puestos (nombre) VALUES ('Gerente');
INSERT INTO puestos (nombre) VALUES ('Subgerente');
INSERT INTO puestos (nombre) VALUES ('Jefe de Departamento');
INSERT INTO puestos (nombre) VALUES ('Supervisor');
INSERT INTO puestos (nombre) VALUES ('Encargado');
INSERT INTO puestos (nombre) VALUES ('Asistente');
INSERT INTO puestos (nombre) VALUES ('Empleado');
INSERT INTO puestos (nombre) VALUES ('Practicante');
INSERT INTO puestos (nombre) VALUES ('Consultor');
INSERT INTO puestos (nombre) VALUES ('Analista');

INSERT INTO estados_pago (nombre) VALUES ('Pendiente');
INSERT INTO estados_pago (nombre) VALUES ('Pagado');
INSERT INTO estados_pago (nombre) VALUES ('Cancelado');
INSERT INTO estados_pago (nombre) VALUES ('Reembolsado');

INSERT INTO estado_envio (nombre) VALUES ('En preparación');
INSERT INTO estado_envio (nombre) VALUES ('Enviado');
INSERT INTO estado_envio (nombre) VALUES ('Entregado');
INSERT INTO estado_envio (nombre) VALUES ('Devuelto');

INSERT INTO estado_devolucion (nombre) VALUES ('Solicitada');
INSERT INTO estado_devolucion (nombre) VALUES ('En proceso');
INSERT INTO estado_devolucion (nombre) VALUES ('Aceptada');
INSERT INTO estado_devolucion (nombre) VALUES ('Rechazada');

INSERT INTO estado_traslados (nombre) VALUES ('En proceso');
INSERT INTO estado_traslados (nombre) VALUES ('En camino');
INSERT INTO estado_traslados (nombre) VALUES ('Entregado');
INSERT INTO estado_traslados (nombre) VALUES ('Cancelado');

INSERT INTO categorias (nombre) VALUES ('Celulares');
INSERT INTO categorias (nombre) VALUES ('Computadoras');
INSERT INTO categorias (nombre) VALUES ('Electrodomésticos');
INSERT INTO categorias (nombre) VALUES ('Ropa');
INSERT INTO categorias (nombre) VALUES ('Zapatos');
INSERT INTO categorias (nombre) VALUES ('Accesorios');
INSERT INTO categorias (nombre) VALUES ('Juguetes');
INSERT INTO categorias (nombre) VALUES ('Libros');
INSERT INTO categorias (nombre) VALUES ('Herramientas');
INSERT INTO categorias (nombre) VALUES ('Muebles');


INSERT INTO empresa_transporte (nombre) VALUES ('Fedex');
INSERT INTO empresa_transporte (nombre) VALUES ('DHL');
INSERT INTO empresa_transporte (nombre) VALUES ('UPS');
INSERT INTO empresa_transporte (nombre) VALUES ('Estafeta');
INSERT INTO empresa_transporte (nombre) VALUES ('Redpack');
INSERT INTO empresa_transporte (nombre) VALUES ('Paquetexpress');
INSERT INTO empresa_transporte (nombre) VALUES ('Correos de México');
INSERT INTO empresa_transporte (nombre) VALUES ('TNT');
INSERT INTO empresa_transporte (nombre) VALUES ('Multipack');
INSERT INTO empresa_transporte (nombre) VALUES ('Estrella Blanca');


COMMIT;