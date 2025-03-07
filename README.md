# Proyecto 1 - Sistema de Gestión para Comercio Electrónico

## Datos del Estudiante
**Nombre:** Irving Fernando Alvarado Asensio  
**Carné:** 202200349  
**Repositorio:** [GitHub](https://github.com/Fercho9134/-SBD1-P1_202200349.git)

## Descripción del Proyecto
Este proyecto tiene como objetivo el diseño y desarrollo de una base de datos relacional optimizada para gestionar un sistema de comercio electrónico de gran escala, similar a plataformas como Amazon o Alibaba. Se implementaron mecanismos para asegurar la integridad y normalización de los datos, permitiendo una gestión eficiente de usuarios, productos, órdenes de compra, pagos, envíos, devoluciones y traslados.

Además, se desarrolló una API utilizando Flask en Python para facilitar la comunicación con la base de datos, lo que permite la inserción y consulta de información en tiempo real. También se incluyó soporte para la carga masiva de datos desde archivos CSV, garantizando flexibilidad en la administración del sistema.

## Objetivos
### Objetivo General
Diseñar e implementar una base de datos relacional eficiente para gestionar las operaciones de un sistema de ventas y distribución, garantizando integridad y normalización en la estructura de datos.

### Objetivos Específicos
- Crear una base de datos relacional optimizada para la gestión de información de la plataforma.
- Implementar procesos de normalización y garantizar integridad referencial.
- Facilitar la carga masiva de datos mediante archivos CSV.
- Desarrollar una API en Flask para la inserción y consulta de datos en la base de datos.
- Diseñar consultas avanzadas en SQL para la generación de informes clave.

## Tecnologías Utilizadas
- **Base de Datos:** Oracle XE (ejecutado en un contenedor Docker)
- **API:** Python con Flask
- **Gestión de Datos:** SQL y archivos CSV
- **Contenerización:** Docker (solo para la base de datos)

## Instrucciones de Instalación y Ejecución
Para probar el proyecto, seguir los siguientes pasos:

### 1. Clonar el Repositorio
```bash
 git clone https://github.com/Fercho9134/-SBD1-P1_202200349.git
 cd -SBD1-P1_202200349
```

### 2. Configurar y Levantar la Base de Datos en Docker
Se utilizará Oracle XE en un contenedor Docker:
```bash
docker run -d --name oracle_db -p 1521:1521 -e ORACLE_ALLOW_REMOTE=true container-registry.oracle.com/database/express:latest
```
Esperar unos minutos hasta que la base de datos esté completamente operativa.

### 3. Ejecutar el Script de Creación de Tablas
Cargar la estructura y datos base en la base de datos ejecutando el script SQL:
```bash
sqlplus system/password@//localhost:1521/XEPDB1 @./sql/script.sql
```

### 4. Configurar y Ejecutar la API en Flask
#### a) Instalar dependencias
```bash
cd api
pip install -r requirements.txt
```
#### b) Ejecutar la API
```bash
python app.py
```

La API estará corriendo en `http://127.0.0.1:5000` y permitirá la comunicación con la base de datos para la gestión de la información.

---