
import cx_Oracle
from app.config import Config


def get_connection():
    try:
        # Crear la conexión
        dsn = cx_Oracle.makedsn(host=Config.ORACLE_HOST, port=Config.ORACLE_PORT, sid=Config.ORACLE_SID)

        # Conectar a la base de datos
        connection = cx_Oracle.connect(user=Config.ORACLE_USER, password=Config.ORACLE_PASSWORD, dsn=dsn, encoding="UTF-8")
        # Si todo va bien, retornar la conexión
        return connection
    except Exception as e:
        # Si ocurre un error, imprimir y devolver None
        print(f"Ocurrió un error al conectar a Oracle: {str(e)}")
        return None

