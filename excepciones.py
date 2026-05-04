# =============================================================================
# ARCHIVO: excepciones.py
# DESCRIPCIÓN: Define todas las excepciones personalizadas del sistema.
#
# ¿Por qué excepciones personalizadas?
# Porque en lugar de recibir un error genérico como "ValueError", el sistema
# lanza errores con nombres claros que dicen exactamente qué salió mal.
# Ejemplo: ClienteInvalidoError es más claro que ValueError.
# =============================================================================


# -----------------------------------------------------------------------------
# EXCEPCIÓN BASE DEL SISTEMA
# Todas las excepciones del sistema heredan de esta.
# Esto nos permite capturar CUALQUIER error del sistema con un solo except.
# -----------------------------------------------------------------------------
class SistemaFJError(Exception):
    """
    Excepción base de Software FJ.
    Hereda de Exception (la clase base de Python para errores).
    """

    def __init__(self, mensaje, codigo=None):
        # Llamamos al constructor del padre (Exception) con el mensaje
        super().__init__(mensaje)
        self.mensaje = mensaje      # Guardamos el mensaje legible
        self.codigo = codigo        # Código opcional para identificar el error

    def __str__(self):
        # Define cómo se ve el error cuando se imprime
        if self.codigo:
            return f"[Código {self.codigo}] {self.mensaje}"
        return self.mensaje


# -----------------------------------------------------------------------------
# ERRORES RELACIONADOS CON CLIENTES
# -----------------------------------------------------------------------------
class ClienteInvalidoError(SistemaFJError):
    """
    Se lanza cuando los datos de un cliente no son válidos.
    Ejemplos: nombre vacío, email sin @, teléfono con letras.
    """
    def __init__(self, mensaje, campo=None):
        super().__init__(mensaje, codigo="CLI-001")
        self.campo = campo  # Campo específico que falló (ej: "email")


class ClienteDuplicadoError(SistemaFJError):
    """
    Se lanza cuando se intenta registrar un cliente que ya existe.
    """
    def __init__(self, id_cliente):
        super().__init__(
            f"El cliente con ID '{id_cliente}' ya está registrado.",
            codigo="CLI-002"
        )
        self.id_cliente = id_cliente


# -----------------------------------------------------------------------------
# ERRORES RELACIONADOS CON SERVICIOS
# -----------------------------------------------------------------------------
class ServicioInvalidoError(SistemaFJError):
    """
    Se lanza cuando los parámetros de un servicio no son válidos.
    Ejemplos: capacidad negativa, tipo de equipo inexistente.
    """
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="SRV-001")


class ServicioNoDisponibleError(SistemaFJError):
    """
    Se lanza cuando se intenta usar un servicio que no está disponible.
    Ejemplo: una sala que ya está reservada en ese horario.
    """
    def __init__(self, nombre_servicio):
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible.",
            codigo="SRV-002"
        )
        self.nombre_servicio = nombre_servicio


# -----------------------------------------------------------------------------
# ERRORES RELACIONADOS CON RESERVAS
# -----------------------------------------------------------------------------
class ReservaInvalidaError(SistemaFJError):
    """
    Se lanza cuando los datos de una reserva no son válidos.
    Ejemplos: duración negativa, estado incorrecto.
    """
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="RES-001")


class ReservaNoEncontradaError(SistemaFJError):
    """
    Se lanza cuando se busca una reserva que no existe en el sistema.
    """
    def __init__(self, id_reserva):
        super().__init__(
            f"No se encontró la reserva con ID '{id_reserva}'.",
            codigo="RES-002"
        )
        self.id_reserva = id_reserva


class OperacionNoPermitidaError(SistemaFJError):
    """
    Se lanza cuando se intenta hacer algo que no está permitido.
    Ejemplo: cancelar una reserva que ya fue cancelada.
    """
    def __init__(self, operacion, razon):
        super().__init__(
            f"Operación '{operacion}' no permitida: {razon}",
            codigo="OPR-001"
        )
        self.operacion = operacion
