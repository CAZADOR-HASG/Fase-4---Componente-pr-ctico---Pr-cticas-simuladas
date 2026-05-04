# =============================================================================
# ARCHIVO: gestor.py
# DESCRIPCIÓN: GestorSistema administra las listas de clientes, servicios
#              y reservas. Es el "cerebro" del sistema.
#
# Funciones principales:
#   - Registrar clientes y servicios
#   - Crear y gestionar reservas
#   - Buscar, listar y reportar
#   - Manejar todos los errores de forma robusta
# =============================================================================

from entidades import Cliente
from servicios import ReservaSala, AlquilerEquipo, Asesoria
from reserva import Reserva
from excepciones import (
    ClienteInvalidoError,
    ClienteDuplicadoError,
    ServicioInvalidoError,
    ReservaInvalidaError,
    ReservaNoEncontradaError,
    OperacionNoPermitidaError,
    SistemaFJError,
)
from logger import logger


class GestorSistema:
    """
    Clase principal que coordina todas las operaciones del sistema Software FJ.
    Mantiene en memoria las listas de clientes, servicios y reservas.
    """

    def __init__(self):
        # Listas internas (en lugar de base de datos)
        self.__clientes  = {}   # dict: id_cliente → objeto Cliente
        self.__servicios = {}   # dict: id_servicio → objeto Servicio
        self.__reservas  = {}   # dict: id_reserva → objeto Reserva

        # Contador de operaciones para estadísticas
        self.__total_operaciones = 0
        self.__operaciones_exitosas = 0
        self.__operaciones_fallidas = 0

        logger.info("Sistema Software FJ iniciado correctamente.")
        print("=" * 55)
        print("   SISTEMA SOFTWARE FJ — GESTIÓN DE SERVICIOS")
        print("=" * 55)

    # =========================================================================
    # GESTIÓN DE CLIENTES
    # =========================================================================

    def registrar_cliente(self, id_cliente, nombre, email, telefono):
        """
        Registra un nuevo cliente en el sistema.
        Demuestra: try/except/else/finally
        """
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Registrando cliente: {nombre}...")

        try:
            # Verificar que no exista ya
            if id_cliente in self.__clientes:
                raise ClienteDuplicadoError(id_cliente)

            # Crear el cliente (puede lanzar ClienteInvalidoError)
            cliente = Cliente(id_cliente, nombre, email, telefono)

        except ClienteDuplicadoError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Registro fallido: {e}")
            print(f"  ❌ Error: {e}")
            return None

        except ClienteInvalidoError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Datos inválidos para cliente {id_cliente}: {e} (campo: {e.campo})")
            print(f"  ❌ Error en campo '{e.campo}': {e}")
            return None

        except Exception as e:
            self.__operaciones_fallidas += 1
            logger.critical(f"Error inesperado registrando cliente: {e}")
            print(f"  ❌ Error inesperado: {e}")
            return None

        else:
            # Solo si no hubo errores
            self.__clientes[id_cliente] = cliente
            self.__operaciones_exitosas += 1
            logger.info(f"Cliente {id_cliente} registrado exitosamente.")
            print(f"  ✅ Cliente '{nombre}' registrado con ID: {id_cliente}")
            return cliente

        finally:
            logger.debug(f"Fin registro cliente {id_cliente}. "
                         f"Total clientes: {len(self.__clientes)}")

    # =========================================================================
    # GESTIÓN DE SERVICIOS
    # =========================================================================

    def registrar_sala(self, id_servicio, nombre_sala, tipo_sala, capacidad):
        """Registra una sala de reuniones en el sistema."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Registrando sala: {nombre_sala}...")

        try:
            sala = ReservaSala(id_servicio, nombre_sala, tipo_sala, capacidad)
            # Validamos los parámetros con una duración de prueba (1 hora)
            sala.validar_parametros(1)
            self.__servicios[id_servicio] = sala
            self.__operaciones_exitosas += 1
            print(f"  ✅ Sala '{nombre_sala}' registrada con ID: {id_servicio}")
            return sala

        except ServicioInvalidoError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Sala inválida {id_servicio}: {e}")
            print(f"  ❌ Error creando sala: {e}")
            return None

        except Exception as e:
            self.__operaciones_fallidas += 1
            logger.critical(f"Error inesperado registrando sala: {e}")
            print(f"  ❌ Error inesperado: {e}")
            return None

    def registrar_equipo(self, id_servicio, tipo_equipo, cantidad):
        """Registra un servicio de alquiler de equipos."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Registrando equipo: {tipo_equipo}...")

        try:
            equipo = AlquilerEquipo(id_servicio, tipo_equipo, cantidad)
            equipo.validar_parametros(1, 1)
            self.__servicios[id_servicio] = equipo
            self.__operaciones_exitosas += 1
            print(f"  ✅ Equipo '{tipo_equipo}' registrado con ID: {id_servicio}")
            return equipo

        except ServicioInvalidoError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Equipo inválido {id_servicio}: {e}")
            print(f"  ❌ Error creando equipo: {e}")
            return None

        except Exception as e:
            self.__operaciones_fallidas += 1
            logger.critical(f"Error inesperado registrando equipo: {e}")
            print(f"  ❌ Error inesperado: {e}")
            return None

    def registrar_asesoria(self, id_servicio, especialidad, consultor):
        """Registra un servicio de asesoría especializada."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Registrando asesoría: {especialidad}...")

        try:
            asesoria = Asesoria(id_servicio, especialidad, consultor)
            asesoria.validar_parametros(1)
            self.__servicios[id_servicio] = asesoria
            self.__operaciones_exitosas += 1
            print(f"  ✅ Asesoría '{especialidad}' registrada con ID: {id_servicio}")
            return asesoria

        except ServicioInvalidoError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Asesoría inválida {id_servicio}: {e}")
            print(f"  ❌ Error creando asesoría: {e}")
            return None

        except Exception as e:
            self.__operaciones_fallidas += 1
            logger.critical(f"Error inesperado registrando asesoría: {e}")
            print(f"  ❌ Error inesperado: {e}")
            return None

    # =========================================================================
    # GESTIÓN DE RESERVAS
    # =========================================================================

    def crear_reserva(self, id_reserva, id_cliente, id_servicio,
                      duracion, descuento=0, con_impuesto=False, notas=""):
        """
        Crea y confirma una reserva completa.
        Demuestra el flujo completo con manejo de excepciones encadenadas.
        """
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Creando reserva {id_reserva}...")

        try:
            # 1. Buscar el cliente
            if id_cliente not in self.__clientes:
                raise ReservaInvalidaError(
                    f"No existe cliente con ID '{id_cliente}'."
                )
            cliente = self.__clientes[id_cliente]

            # 2. Buscar el servicio
            if id_servicio not in self.__servicios:
                raise ReservaInvalidaError(
                    f"No existe servicio con ID '{id_servicio}'."
                )
            servicio = self.__servicios[id_servicio]

            # 3. Crear el objeto Reserva
            reserva = Reserva(id_reserva, cliente, servicio, duracion, notas)

            # 4. Confirmar la reserva (aquí pueden ocurrir más excepciones)
            reserva.confirmar(descuento=descuento, con_impuesto=con_impuesto)

            # 5. Guardar en la lista
            self.__reservas[id_reserva] = reserva
            self.__operaciones_exitosas += 1
            return reserva

        except ReservaInvalidaError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Reserva {id_reserva} fallida: {e}")
            print(f"  ❌ Error en reserva: {e}")
            return None

        except OperacionNoPermitidaError as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Operación no permitida en {id_reserva}: {e}")
            print(f"  ❌ Operación no permitida: {e}")
            return None

        except SistemaFJError as e:
            # Captura cualquier error del sistema no contemplado arriba
            self.__operaciones_fallidas += 1
            logger.error(f"Error del sistema en reserva {id_reserva}: {e}")
            print(f"  ❌ Error del sistema: {e}")
            return None

        except Exception as e:
            self.__operaciones_fallidas += 1
            logger.critical(f"Error crítico inesperado en reserva {id_reserva}: {e}")
            print(f"  ❌ Error crítico: {e}")
            return None

    def cancelar_reserva(self, id_reserva, motivo="Sin motivo"):
        """Cancela una reserva existente."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Cancelando reserva {id_reserva}...")

        try:
            if id_reserva not in self.__reservas:
                raise ReservaNoEncontradaError(id_reserva)
            self.__reservas[id_reserva].cancelar(motivo)
            self.__operaciones_exitosas += 1

        except ReservaNoEncontradaError as e:
            self.__operaciones_fallidas += 1
            logger.error(str(e))
            print(f"  ❌ {e}")

        except OperacionNoPermitidaError as e:
            self.__operaciones_fallidas += 1
            logger.warning(str(e))
            print(f"  ⚠️ {e}")

    # =========================================================================
    # CONSULTAS Y REPORTES
    # =========================================================================

    def listar_clientes(self):
        """Muestra todos los clientes registrados."""
        print("\n" + "─" * 55)
        print("  CLIENTES REGISTRADOS")
        print("─" * 55)
        if not self.__clientes:
            print("  (No hay clientes registrados)")
            return
        for cliente in self.__clientes.values():
            print(f"  • {cliente}")

    def listar_servicios(self):
        """Muestra todos los servicios disponibles."""
        print("\n" + "─" * 55)
        print("  SERVICIOS REGISTRADOS")
        print("─" * 55)
        if not self.__servicios:
            print("  (No hay servicios registrados)")
            return
        for servicio in self.__servicios.values():
            servicio.mostrar_info()

    def listar_reservas(self):
        """Muestra todas las reservas con su estado."""
        print("\n" + "─" * 55)
        print("  RESERVAS DEL SISTEMA")
        print("─" * 55)
        if not self.__reservas:
            print("  (No hay reservas registradas)")
            return
        for reserva in self.__reservas.values():
            reserva.mostrar_info()

    def mostrar_estadisticas(self):
        """Muestra un resumen de las operaciones del sistema."""
        print("\n" + "=" * 55)
        print("  ESTADÍSTICAS DEL SISTEMA")
        print("=" * 55)
        print(f"  Total operaciones   : {self.__total_operaciones}")
        print(f"  Operaciones exitosas: {self.__operaciones_exitosas}")
        print(f"  Operaciones fallidas: {self.__operaciones_fallidas}")
        print(f"  Clientes registrados: {len(self.__clientes)}")
        print(f"  Servicios activos   : {len(self.__servicios)}")
        print(f"  Reservas totales    : {len(self.__reservas)}")
        confirmadas = sum(
            1 for r in self.__reservas.values()
            if r.estado == "CONFIRMADA"
        )
        canceladas = sum(
            1 for r in self.__reservas.values()
            if r.estado == "CANCELADA"
        )
        print(f"  Reservas confirmadas: {confirmadas}")
        print(f"  Reservas canceladas : {canceladas}")
        print("=" * 55)
        logger.info("Estadísticas del sistema consultadas.")
