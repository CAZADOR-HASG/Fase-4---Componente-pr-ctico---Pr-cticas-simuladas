# =============================================================================
# ARCHIVO: reserva.py
# DESCRIPCIÓN: Define la clase Reserva que integra cliente + servicio.
#
# Conceptos demostrados:
#   - Integración de objetos (composición)
#   - Máquina de estados: PENDIENTE → CONFIRMADA → CANCELADA
#   - try/except, try/except/else, try/except/finally
#   - Encadenamiento de excepciones (raise X from Y)
# =============================================================================

from entidades import EntidadBase
from excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ClienteInvalidoError,
)
from logger import logger


# Estados posibles de una reserva (usamos constantes para evitar errores de tipeo)
ESTADO_PENDIENTE   = "PENDIENTE"
ESTADO_CONFIRMADA  = "CONFIRMADA"
ESTADO_CANCELADA   = "CANCELADA"


class Reserva(EntidadBase):
    """
    Representa una reserva en el sistema Software FJ.
    Integra: un Cliente + un Servicio + duración + estado.
    """

    def __init__(self, id_reserva, cliente, servicio, duracion, notas=""):
        """
        Crea una reserva en estado PENDIENTE.

        Parámetros:
            id_reserva: str     → identificador único (ej: "RES001")
            cliente   : Cliente → objeto Cliente previamente creado
            servicio  : Servicio→ objeto Servicio (Sala, Equipo o Asesoría)
            duracion  : int/float → horas/días/sesiones según el servicio
            notas     : str     → observaciones opcionales
        """
        super().__init__(id_reserva)

        # Guardamos las referencias a los objetos
        self.__cliente  = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__notas    = notas

        # Estado inicial siempre es PENDIENTE
        self.__estado = ESTADO_PENDIENTE

        # El costo se calcula al confirmar, no al crear
        self.__costo_total = 0.0

        logger.info(
            f"Reserva creada: {id_reserva} | "
            f"Cliente: {cliente.id_entidad} | "
            f"Servicio: {servicio.id_entidad} | "
            f"Duración: {duracion}"
        )

    # ── Getters ────────────────────────────────────────────────────────
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    @property
    def notas(self):
        return self.__notas

    # ── Métodos abstractos implementados ──────────────────────────────

    def validar(self):
        """Valida que la reserva sea procesable."""
        return self.__estado == ESTADO_PENDIENTE

    def mostrar_info(self):
        """Muestra el detalle completo de la reserva."""
        print(f"""
  ┌── Reserva ──────────────────────────────────────┐
  │ ID Reserva : {self.id_entidad}
  │ Estado     : {self.__estado}
  │ Cliente    : {self.__cliente.id_entidad} - {self.__cliente.nombre}
  │ Servicio   : {self.__servicio.id_entidad} - {self.__servicio.nombre}
  │ Duración   : {self.__duracion}
  │ Costo total: ${self.__costo_total:,.0f}
  │ Notas      : {self.__notas or "Sin notas"}
  │ Creada el  : {self.obtener_fecha_str()}
  └─────────────────────────────────────────────────┘""")

    # ── Lógica de negocio ─────────────────────────────────────────────

    def confirmar(self, descuento=0, con_impuesto=False):
        """
        Confirma la reserva, calculando y guardando el costo final.

        Demuestra: try/except/else/finally
            - try     : intenta confirmar
            - except  : captura errores específicos
            - else    : se ejecuta SOLO si no hubo error
            - finally : se ejecuta SIEMPRE (con o sin error)

        Parámetros:
            descuento   : float → porcentaje de descuento
            con_impuesto: bool  → si se aplica IVA
        """
        logger.info(f"Intentando confirmar reserva {self.id_entidad}...")

        try:
            # 1. Verificar que la reserva esté en estado PENDIENTE
            if self.__estado != ESTADO_PENDIENTE:
                raise OperacionNoPermitidaError(
                    "confirmar",
                    f"la reserva ya está en estado '{self.__estado}'"
                )

            # 2. Verificar que el cliente esté activo
            if not self.__cliente.validar():
                raise ClienteInvalidoError(
                    f"El cliente {self.__cliente.id_entidad} no está activo."
                )

            # 3. Verificar que el servicio esté disponible
            # Este método lanza ServicioNoDisponibleError si no está disponible
            self.__servicio.verificar_disponibilidad()

            # 4. Calcular el costo total (puede lanzar ServicioInvalidoError)
            self.__costo_total = self.__servicio.calcular_costo(
                duracion=self.__duracion,
                descuento=descuento,
                con_impuesto=con_impuesto
            )

            # 5. Cambiar el estado a CONFIRMADA
            self.__estado = ESTADO_CONFIRMADA

        except OperacionNoPermitidaError as e:
            # Error de lógica de negocio → lo registramos y relanzamos
            logger.error(f"Reserva {self.id_entidad} - {e}")
            raise   # Volvemos a lanzar la excepción para que el llamador la maneje

        except (ServicioNoDisponibleError, ClienteInvalidoError) as e:
            # Error en cliente o servicio → encadenamos la excepción
            logger.error(f"Reserva {self.id_entidad} no confirmada: {e}")
            # raise X from Y: encadena la causa original con el nuevo error
            raise ReservaInvalidaError(
                f"No se pudo confirmar la reserva {self.id_entidad}: {e}"
            ) from e

        except Exception as e:
            # Cualquier otro error inesperado
            logger.critical(f"Error inesperado al confirmar {self.id_entidad}: {e}")
            raise ReservaInvalidaError(
                f"Error inesperado al confirmar la reserva: {e}"
            ) from e

        else:
            # Este bloque SOLO se ejecuta si NO hubo ninguna excepción
            logger.info(
                f"Reserva {self.id_entidad} CONFIRMADA | "
                f"Costo: ${self.__costo_total:,.0f}"
            )
            print(f"  ✅ Reserva {self.id_entidad} confirmada. "
                  f"Costo total: ${self.__costo_total:,.0f}")

        finally:
            # Este bloque se ejecuta SIEMPRE, haya error o no
            # Útil para liberar recursos, cerrar conexiones, etc.
            logger.debug(
                f"Proceso de confirmación de {self.id_entidad} finalizado. "
                f"Estado actual: {self.__estado}"
            )

    def cancelar(self, motivo="Sin motivo especificado"):
        """
        Cancela la reserva si está en estado PENDIENTE o CONFIRMADA.

        Demuestra: try/except/finally
        """
        logger.info(f"Intentando cancelar reserva {self.id_entidad}...")

        try:
            # No se puede cancelar lo que ya fue cancelado
            if self.__estado == ESTADO_CANCELADA:
                raise OperacionNoPermitidaError(
                    "cancelar",
                    "la reserva ya estaba cancelada"
                )

            # Guardamos el estado anterior para el log
            estado_anterior = self.__estado
            self.__estado = ESTADO_CANCELADA
            self.__notas += f" | Cancelada: {motivo}"

        except OperacionNoPermitidaError as e:
            logger.warning(f"Cancelación inválida en {self.id_entidad}: {e}")
            raise   # Relanzamos para que el llamador decida qué hacer

        finally:
            # Se ejecuta siempre
            logger.debug(f"Proceso de cancelación de {self.id_entidad} terminado.")

        # Si llegamos aquí, la cancelación fue exitosa
        logger.info(
            f"Reserva {self.id_entidad} CANCELADA | Motivo: {motivo}"
        )
        print(f"  🚫 Reserva {self.id_entidad} cancelada. Motivo: {motivo}")

    def procesar(self):
        """
        Procesa la reserva: la confirma si está pendiente.
        Demuestra un flujo completo de manejo de excepciones.
        """
        try:
            self.confirmar()
        except ReservaInvalidaError as e:
            logger.error(f"No se pudo procesar {self.id_entidad}: {e}")
            print(f"  ❌ Error al procesar reserva {self.id_entidad}: {e}")
            return False
        return True

    def __str__(self):
        return (f"Reserva({self.id_entidad}, "
                f"cliente={self.__cliente.id_entidad}, "
                f"servicio={self.__servicio.id_entidad}, "
                f"estado={self.__estado}, "
                f"costo=${self.__costo_total:,.0f})")
