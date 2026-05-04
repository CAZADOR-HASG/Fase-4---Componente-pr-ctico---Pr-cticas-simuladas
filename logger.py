# =============================================================================
# ARCHIVO: logger.py
# DESCRIPCIÓN: Configura el sistema de registro de eventos y errores (logs).
#
# ¿Qué es un log?
# Es un archivo de texto donde se guarda un registro de todo lo que pasa
# en el sistema: errores, operaciones exitosas, advertencias, etc.
# Cada línea tiene fecha, hora, nivel de gravedad y el mensaje.
#
# Ejemplo de línea en el log:
# 2026-05-01 10:23:45 | ERROR    | Cliente inválido: email sin @
# 2026-05-01 10:23:46 | INFO     | Reserva R001 confirmada exitosamente
# =============================================================================

import logging    # Módulo estándar de Python para logs
import os         # Para manejar rutas de archivos


def configurar_logger(nombre="SistemaFJ", archivo_log="sistema_fj.log"):
    """
    Crea y configura el logger del sistema.

    Parámetros:
        nombre     : Nombre del logger (aparece en cada línea del log)
        archivo_log: Nombre del archivo donde se guardan los logs

    Retorna:
        logger: El objeto logger listo para usar
    """

    # Creamos el logger con el nombre dado
    logger = logging.getLogger(nombre)

    # Evitar duplicar handlers si la función se llama más de una vez
    if logger.handlers:
        return logger

    # Nivel mínimo de mensajes a registrar (DEBUG captura todo)
    logger.setLevel(logging.DEBUG)

    # ------------------------------------------------------------------
    # FORMATO del mensaje en el archivo de log
    # %(asctime)s   → Fecha y hora del evento
    # %(levelname)  → Nivel: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # %(message)s   → El texto del mensaje
    # ------------------------------------------------------------------
    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ------------------------------------------------------------------
    # HANDLER 1: Escribe los logs en un ARCHIVO
    # mode='a' significa "append" → agrega sin borrar lo anterior
    # encoding='utf-8' para soportar tildes y caracteres especiales
    # ------------------------------------------------------------------
    handler_archivo = logging.FileHandler(
        filename=archivo_log,
        mode='a',
        encoding='utf-8'
    )
    handler_archivo.setLevel(logging.DEBUG)   # Guarda todo en el archivo
    handler_archivo.setFormatter(formato)

    # ------------------------------------------------------------------
    # HANDLER 2: Muestra los logs en la CONSOLA (pantalla)
    # Solo mostramos WARNING o superior en consola para no saturar
    # ------------------------------------------------------------------
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.WARNING)  # Solo errores en consola
    handler_consola.setFormatter(formato)

    # Agregamos ambos handlers al logger
    logger.addHandler(handler_archivo)
    logger.addHandler(handler_consola)

    return logger


# Creamos una instancia global del logger para usar en todo el sistema
logger = configurar_logger()
