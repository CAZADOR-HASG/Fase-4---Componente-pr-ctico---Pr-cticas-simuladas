

# =============================================================================
# SOFTWARE FJ — SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS
# Curso: Programación 213023 — UNAD
# Descripción: Sistema orientado a objetos sin base de datos que gestiona
#              clientes, servicios y reservas con manejo robusto de excepciones.
#
# Contenido (en orden de dependencia):
#   1. Imports globales
#   2. Excepciones personalizadas
#   3. Logger (sistema de logs)
#   4. EntidadBase (clase abstracta raíz)
#   5. Cliente
#   6. Servicio (abstracta) + ReservaSala, AlquilerEquipo, Asesoria
#   7. Reserva
#   8. GestorSistema
#   9. main() — simulación de 21 operaciones
# =============================================================================


# =============================================================================
# 1. IMPORTS GLOBALES
# Solo se importan una vez aquí arriba para todo el archivo.
# =============================================================================
import logging           # Para el sistema de logs
import os                # Para manejo de rutas
import re                # Para validar email con expresiones regulares
from abc import ABC, abstractmethod   # Para clases abstractas
from datetime import datetime         # Para fechas de creación


# =============================================================================
# 2. EXCEPCIONES PERSONALIZADAS
# =============================================================================

class SistemaFJError(Exception):
    """
    Excepción base de Software FJ.
    Todas las demás excepciones del sistema heredan de esta.
    Esto permite capturar cualquier error del sistema con un solo except.
    """
    def __init__(self, mensaje, codigo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje      # Mensaje legible del error
        self.codigo  = codigo       # Código opcional para identificar el error

    def __str__(self):
        if self.codigo:
            return f"[Código {self.codigo}] {self.mensaje}"
        return self.mensaje


class ClienteInvalidoError(SistemaFJError):
    """Se lanza cuando los datos de un cliente no son válidos."""
    def __init__(self, mensaje, campo=None):
        super().__init__(mensaje, codigo="CLI-001")
        self.campo = campo   # Campo específico que falló (ej: "email")


class ClienteDuplicadoError(SistemaFJError):
    """Se lanza cuando se intenta registrar un cliente que ya existe."""
    def __init__(self, id_cliente):
        super().__init__(
            f"El cliente con ID '{id_cliente}' ya está registrado.",
            codigo="CLI-002"
        )
        self.id_cliente = id_cliente


class ServicioInvalidoError(SistemaFJError):
    """Se lanza cuando los parámetros de un servicio no son válidos."""
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="SRV-001")


class ServicioNoDisponibleError(SistemaFJError):
    """Se lanza cuando se intenta usar un servicio no disponible."""
    def __init__(self, nombre_servicio):
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible.",
            codigo="SRV-002"
        )
        self.nombre_servicio = nombre_servicio


class ReservaInvalidaError(SistemaFJError):
    """Se lanza cuando los datos de una reserva no son válidos."""
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo="RES-001")


class ReservaNoEncontradaError(SistemaFJError):
    """Se lanza cuando se busca una reserva que no existe."""
    def __init__(self, id_reserva):
        super().__init__(
            f"No se encontró la reserva con ID '{id_reserva}'.",
            codigo="RES-002"
        )
        self.id_reserva = id_reserva


class OperacionNoPermitidaError(SistemaFJError):
    """Se lanza cuando se intenta una operación no permitida."""
    def __init__(self, operacion, razon):
        super().__init__(
            f"Operación '{operacion}' no permitida: {razon}",
            codigo="OPR-001"
        )
        self.operacion = operacion


# =============================================================================
# 3. LOGGER — SISTEMA DE REGISTRO DE EVENTOS
# =============================================================================

def configurar_logger(nombre="SistemaFJ", archivo_log="sistema_fj.log"):
    """
    Crea y configura el logger del sistema.
    Escribe en archivo (todos los niveles) y en consola (solo WARNING+).
    """
    logger = logging.getLogger(nombre)

    # Evitar duplicar handlers si la función se llama más de una vez
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Formato: fecha | nivel | mensaje
    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler 1: escribe TODO en el archivo de log
    handler_archivo = logging.FileHandler(
        filename=archivo_log, mode='a', encoding='utf-8'
    )
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    # Handler 2: muestra solo WARNING o superior en consola
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.WARNING)
    handler_consola.setFormatter(formato)

    logger.addHandler(handler_archivo)
    logger.addHandler(handler_consola)
    return logger


# Instancia global del logger — se usa en todo el sistema
logger = configurar_logger()


# =============================================================================
# 4. ENTIDAD BASE — CLASE ABSTRACTA RAÍZ
# =============================================================================

class EntidadBase(ABC):
    """
    Clase abstracta raíz de todas las entidades del sistema.
    Obliga a que toda entidad tenga un ID, fecha de creación,
    y los métodos mostrar_info() y validar().
    """
    def __init__(self, id_entidad):
        self.__id_entidad    = id_entidad
        self.__fecha_creacion = datetime.now()

    @property
    def id_entidad(self):
        """Retorna el ID de la entidad (solo lectura)."""
        return self.__id_entidad

    @property
    def fecha_creacion(self):
        """Retorna la fecha de creación (solo lectura)."""
        return self.__fecha_creacion

    @abstractmethod
    def mostrar_info(self):
        """Muestra la información completa de la entidad."""
        pass

    @abstractmethod
    def validar(self):
        """Valida que los datos de la entidad sean correctos."""
        pass

    def obtener_fecha_str(self):
        """Retorna la fecha de creación como texto legible."""
        return self.__fecha_creacion.strftime("%d/%m/%Y %H:%M:%S")


# =============================================================================
# 5. CLASE CLIENTE
# =============================================================================

class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.
    Aplica encapsulación estricta: todos los atributos son privados (__)
    y se acceden solo mediante @property (getters) y setters con validación.
    """
    def __init__(self, id_cliente, nombre, email, telefono):
        super().__init__(id_cliente)
        # Los setters validan automáticamente al asignar
        self.nombre   = nombre
        self.email    = email
        self.telefono = telefono
        self.__activo = True
        logger.info(f"Cliente creado: {id_cliente} - {nombre}")

    # ── Getters ──────────────────────────────────────────────────────────────
    @property
    def nombre(self):
        return self.__nombre

    @property
    def email(self):
        return self.__email

    @property
    def telefono(self):
        return self.__telefono

    @property
    def activo(self):
        return self.__activo

    # ── Setters con validación ───────────────────────────────────────────────
    @nombre.setter
    def nombre(self, valor):
        """Nombre: no vacío, mínimo 3 caracteres, solo letras y espacios."""
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El nombre no puede estar vacío.", campo="nombre")
        if len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.", campo="nombre")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", valor.strip()):
            raise ClienteInvalidoError("El nombre solo puede contener letras y espacios.", campo="nombre")
        self.__nombre = valor.strip().title()

    @email.setter
    def email(self, valor):
        """Email: formato válido (algo@algo.algo)."""
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El email no puede estar vacío.", campo="email")
        patron = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron, valor.strip()):
            raise ClienteInvalidoError(
                f"El email '{valor}' no tiene un formato válido.", campo="email"
            )
        self.__email = valor.strip().lower()

    @telefono.setter
    def telefono(self, valor):
        """Teléfono: entre 7 y 10 dígitos numéricos."""
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El teléfono no puede estar vacío.", campo="telefono")
        solo_digitos = re.sub(r"[\s\-\(\)]", "", valor.strip())
        if not solo_digitos.isdigit():
            raise ClienteInvalidoError("El teléfono solo puede contener números.", campo="telefono")
        if not (7 <= len(solo_digitos) <= 10):
            raise ClienteInvalidoError("El teléfono debe tener entre 7 y 10 dígitos.", campo="telefono")
        self.__telefono = solo_digitos

    # ── Métodos abstractos implementados ────────────────────────────────────
    def validar(self):
        """Retorna True si el cliente está activo y puede operar."""
        if not self.__activo:
            logger.warning(f"Cliente {self.id_entidad} inactivo intentó operar.")
            return False
        return True

    def mostrar_info(self):
        estado = "Activo" if self.__activo else "Inactivo"
        print(f"""
┌─────────────────────────────────────────┐
│            FICHA DE CLIENTE             │
├─────────────────────────────────────────┤
│ ID       : {self.id_entidad:<30} │
│ Nombre   : {self.__nombre:<30} │
│ Email    : {self.__email:<30} │
│ Teléfono : {self.__telefono:<30} │
│ Estado   : {estado:<30} │
│ Registro : {self.obtener_fecha_str():<30} │
└─────────────────────────────────────────┘""")

    def desactivar(self):
        """Desactiva el cliente impidiendo nuevas reservas."""
        self.__activo = False
        logger.info(f"Cliente {self.id_entidad} desactivado.")

    def __str__(self):
        return f"Cliente({self.id_entidad}, {self.__nombre}, {self.__email})"

    def __repr__(self):
        return (f"Cliente(id='{self.id_entidad}', nombre='{self.__nombre}', "
                f"email='{self.__email}', tel='{self.__telefono}')")


# =============================================================================
# 6. SERVICIOS — CLASE ABSTRACTA + TRES ESPECIALIZACIONES
# =============================================================================

class Servicio(EntidadBase):
    """
    Clase abstracta que define el contrato para todos los servicios.
    Hereda de EntidadBase y agrega comportamiento específico de servicios.
    """
    def __init__(self, id_servicio, nombre, descripcion, disponible=True):
        super().__init__(id_servicio)
        self.__nombre      = nombre
        self.__descripcion = descripcion
        self.__disponible  = disponible

    @property
    def nombre(self):
        return self.__nombre

    @property
    def descripcion(self):
        return self.__descripcion

    @property
    def disponible(self):
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        self.__disponible = bool(valor)

    @abstractmethod
    def calcular_costo(self, duracion, descuento=0, con_impuesto=False):
        """Calcula el costo del servicio según su tipo."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida que la duración y parámetros sean correctos."""
        pass

    def verificar_disponibilidad(self):
        """Lanza ServicioNoDisponibleError si el servicio no está activo."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)
        return True

    def validar(self):
        return self.__disponible

    def mostrar_info(self):
        estado = "✅ Disponible" if self.__disponible else "❌ No disponible"
        print(f"  Servicio [{self.id_entidad}]: {self.__nombre} — {estado}")


# ── SERVICIO 1: RESERVA DE SALA ──────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones.
    La duración se mide en HORAS.
    Costo = precio_hora × horas
    """
    PRECIOS_POR_CAPACIDAD = {
        "pequeña":   25000,
        "mediana":   45000,
        "grande":    80000,
        "auditorio": 150000,
    }

    def __init__(self, id_servicio, nombre_sala, tipo_sala, capacidad_maxima):
        self.__nombre_sala     = nombre_sala
        self.__tipo_sala       = tipo_sala.lower()
        self.__capacidad_maxima = capacidad_maxima
        self.__precio_hora     = self.PRECIOS_POR_CAPACIDAD.get(self.__tipo_sala, 0)
        super().__init__(
            id_servicio=id_servicio,
            nombre=f"Sala: {nombre_sala}",
            descripcion=f"Sala {tipo_sala} para {capacidad_maxima} personas"
        )
        logger.info(f"Servicio creado: ReservaSala [{id_servicio}] - {nombre_sala}")

    @property
    def precio_hora(self):
        return self.__precio_hora

    @property
    def capacidad_maxima(self):
        return self.__capacidad_maxima

    def validar_parametros(self, duracion):
        if self.__tipo_sala not in self.PRECIOS_POR_CAPACIDAD:
            raise ServicioInvalidoError(
                f"Tipo de sala '{self.__tipo_sala}' no existe. "
                f"Opciones: {list(self.PRECIOS_POR_CAPACIDAD.keys())}"
            )
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ServicioInvalidoError("La duración (horas) debe ser un número positivo.")
        if duracion > 12:
            raise ServicioInvalidoError("No se puede reservar una sala por más de 12 horas seguidas.")
        return True

    def calcular_costo(self, duracion, descuento=0, con_impuesto=False):
        """
        Fórmula: precio_hora × horas
        Parámetros opcionales para sobrecarga simulada:
            descuento    → porcentaje de descuento (0-100)
            con_impuesto → aplica IVA del 19%
        """
        self.validar_parametros(duracion)
        costo = self.__precio_hora * duracion
        if descuento > 0:
            if not (0 < descuento < 100):
                raise ServicioInvalidoError("El descuento debe estar entre 0 y 100.")
            costo = costo * (1 - descuento / 100)
        if con_impuesto:
            costo = costo * 1.19
        return round(costo, 2)

    def mostrar_info(self):
        print(f"""
  ┌── Reserva de Sala ──────────────────────────────┐
  │ ID         : {self.id_entidad}
  │ Sala       : {self.__nombre_sala}
  │ Tipo       : {self.__tipo_sala.capitalize()}
  │ Capacidad  : {self.__capacidad_maxima} personas
  │ Precio/hora: ${self.__precio_hora:,.0f}
  │ Disponible : {"Sí" if self.disponible else "No"}
  └─────────────────────────────────────────────────┘""")

    def __str__(self):
        return (f"ReservaSala({self.id_entidad}, '{self.__nombre_sala}', "
                f"tipo='{self.__tipo_sala}', cap={self.__capacidad_maxima})")


# ── SERVICIO 2: ALQUILER DE EQUIPO ───────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    La duración se mide en DÍAS.
    Costo = precio_dia × días × cantidad
    """
    PRECIOS_POR_EQUIPO = {
        "laptop":    80000,
        "proyector": 50000,
        "impresora": 30000,
        "servidor":  150000,
        "tablet":    40000,
    }

    def __init__(self, id_servicio, tipo_equipo, cantidad_disponible):
        self.__tipo_equipo        = tipo_equipo.lower()
        self.__cantidad_disponible = cantidad_disponible
        self.__precio_dia         = self.PRECIOS_POR_EQUIPO.get(self.__tipo_equipo, 0)
        super().__init__(
            id_servicio=id_servicio,
            nombre=f"Alquiler: {tipo_equipo.capitalize()}",
            descripcion=f"Alquiler de {tipo_equipo}, {cantidad_disponible} unidades"
        )
        logger.info(f"Servicio creado: AlquilerEquipo [{id_servicio}] - {tipo_equipo}")

    @property
    def tipo_equipo(self):
        return self.__tipo_equipo

    @property
    def cantidad_disponible(self):
        return self.__cantidad_disponible

    @property
    def precio_dia(self):
        return self.__precio_dia

    def validar_parametros(self, duracion, cantidad=1):
        if self.__tipo_equipo not in self.PRECIOS_POR_EQUIPO:
            raise ServicioInvalidoError(
                f"Equipo '{self.__tipo_equipo}' no existe. "
                f"Opciones: {list(self.PRECIOS_POR_EQUIPO.keys())}"
            )
        if not isinstance(duracion, int) or duracion <= 0:
            raise ServicioInvalidoError("La duración (días) debe ser un número entero positivo.")
        if duracion > 30:
            raise ServicioInvalidoError("No se puede alquilar un equipo por más de 30 días.")
        if cantidad > self.__cantidad_disponible:
            raise ServicioInvalidoError(
                f"Solo hay {self.__cantidad_disponible} unidades disponibles "
                f"de {self.__tipo_equipo}. Se solicitaron {cantidad}."
            )
        return True

    def calcular_costo(self, duracion, descuento=0, con_impuesto=False, cantidad=1):
        """
        Fórmula: precio_dia × días × cantidad
        Parámetros opcionales (sobrecarga simulada):
            cantidad     → unidades a alquilar
            descuento    → porcentaje de descuento
            con_impuesto → aplica IVA del 19%
        """
        self.validar_parametros(duracion, cantidad)
        costo = self.__precio_dia * duracion * cantidad
        if descuento > 0:
            if not (0 < descuento < 100):
                raise ServicioInvalidoError("El descuento debe estar entre 0 y 100.")
            costo = costo * (1 - descuento / 100)
        if con_impuesto:
            costo = costo * 1.19
        return round(costo, 2)

    def mostrar_info(self):
        print(f"""
  ┌── Alquiler de Equipo ───────────────────────────┐
  │ ID         : {self.id_entidad}
  │ Equipo     : {self.__tipo_equipo.capitalize()}
  │ Disponibles: {self.__cantidad_disponible} unidades
  │ Precio/día : ${self.__precio_dia:,.0f}
  │ Disponible : {"Sí" if self.disponible else "No"}
  └─────────────────────────────────────────────────┘""")

    def __str__(self):
        return (f"AlquilerEquipo({self.id_entidad}, tipo='{self.__tipo_equipo}', "
                f"cant={self.__cantidad_disponible}, ${self.__precio_dia}/día)")


# ── SERVICIO 3: ASESORÍA ESPECIALIZADA ───────────────────────────────────────

class Asesoria(Servicio):
    """
    Servicio de asesoría especializada por un consultor.
    La duración se mide en número de SESIONES.
    Costo = tarifa_sesion × sesiones
    """
    TARIFAS_POR_ESPECIALIDAD = {
        "python":                  120000,
        "java":                    120000,
        "bases_de_datos":          100000,
        "redes":                   110000,
        "ciberseguridad":          150000,
        "inteligencia_artificial": 200000,
        "gestion_proyectos":        90000,
    }

    def __init__(self, id_servicio, especialidad, nombre_consultor):
        self.__especialidad      = especialidad.lower()
        self.__nombre_consultor  = nombre_consultor
        self.__tarifa_sesion     = self.TARIFAS_POR_ESPECIALIDAD.get(self.__especialidad, 0)
        super().__init__(
            id_servicio=id_servicio,
            nombre=f"Asesoría: {especialidad.replace('_', ' ').title()}",
            descripcion=f"Asesoría en {especialidad} con {nombre_consultor}"
        )
        logger.info(f"Servicio creado: Asesoria [{id_servicio}] - {especialidad}")

    @property
    def especialidad(self):
        return self.__especialidad

    @property
    def nombre_consultor(self):
        return self.__nombre_consultor

    @property
    def tarifa_sesion(self):
        return self.__tarifa_sesion

    def validar_parametros(self, duracion):
        if self.__especialidad not in self.TARIFAS_POR_ESPECIALIDAD:
            raise ServicioInvalidoError(
                f"Especialidad '{self.__especialidad}' no disponible. "
                f"Opciones: {list(self.TARIFAS_POR_ESPECIALIDAD.keys())}"
            )
        if not isinstance(duracion, int) or duracion <= 0:
            raise ServicioInvalidoError("El número de sesiones debe ser un entero positivo.")
        if duracion > 20:
            raise ServicioInvalidoError("No se pueden contratar más de 20 sesiones a la vez.")
        return True

    def calcular_costo(self, duracion, descuento=0, con_impuesto=False):
        """
        Fórmula: tarifa_sesion × sesiones
        Parámetros opcionales (sobrecarga simulada):
            descuento    → porcentaje de descuento
            con_impuesto → aplica IVA del 19%
        """
        self.validar_parametros(duracion)
        costo = self.__tarifa_sesion * duracion
        if descuento > 0:
            if not (0 < descuento < 100):
                raise ServicioInvalidoError("El descuento debe estar entre 0 y 100.")
            costo = costo * (1 - descuento / 100)
        if con_impuesto:
            costo = costo * 1.19
        return round(costo, 2)

    def mostrar_info(self):
        print(f"""
  ┌── Asesoría Especializada ───────────────────────┐
  │ ID          : {self.id_entidad}
  │ Especialidad: {self.__especialidad.replace('_', ' ').title()}
  │ Consultor   : {self.__nombre_consultor}
  │ Tarifa/ses. : ${self.__tarifa_sesion:,.0f}
  │ Disponible  : {"Sí" if self.disponible else "No"}
  └─────────────────────────────────────────────────┘""")

    def __str__(self):
        return (f"Asesoria({self.id_entidad}, '{self.__especialidad}', "
                f"consultor='{self.__nombre_consultor}')")


# =============================================================================
# 7. CLASE RESERVA
# =============================================================================

# Estados posibles de una reserva
ESTADO_PENDIENTE  = "PENDIENTE"
ESTADO_CONFIRMADA = "CONFIRMADA"
ESTADO_CANCELADA  = "CANCELADA"


class Reserva(EntidadBase):
    """
    Representa una reserva: integra Cliente + Servicio + duración + estado.
    Máquina de estados: PENDIENTE → CONFIRMADA → CANCELADA
    Demuestra: try/except/else/finally y encadenamiento de excepciones.
    """
    def __init__(self, id_reserva, cliente, servicio, duracion, notas=""):
        super().__init__(id_reserva)
        self.__cliente   = cliente
        self.__servicio  = servicio
        self.__duracion  = duracion
        self.__notas     = notas
        self.__estado    = ESTADO_PENDIENTE
        self.__costo_total = 0.0
        logger.info(
            f"Reserva creada: {id_reserva} | "
            f"Cliente: {cliente.id_entidad} | "
            f"Servicio: {servicio.id_entidad} | "
            f"Duración: {duracion}"
        )

    # ── Getters ──────────────────────────────────────────────────────────────
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

    # ── Métodos abstractos implementados ────────────────────────────────────
    def validar(self):
        return self.__estado == ESTADO_PENDIENTE

    def mostrar_info(self):
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

    # ── Lógica de negocio ────────────────────────────────────────────────────
    def confirmar(self, descuento=0, con_impuesto=False):
        """
        Confirma la reserva y calcula el costo final.
        Demuestra: try / except / else / finally
        """
        logger.info(f"Intentando confirmar reserva {self.id_entidad}...")
        try:
            # Verificar estado
            if self.__estado != ESTADO_PENDIENTE:
                raise OperacionNoPermitidaError(
                    "confirmar",
                    f"la reserva ya está en estado '{self.__estado}'"
                )
            # Verificar cliente activo
            if not self.__cliente.validar():
                raise ClienteInvalidoError(
                    f"El cliente {self.__cliente.id_entidad} no está activo."
                )
            # Verificar disponibilidad del servicio
            self.__servicio.verificar_disponibilidad()

            # Calcular costo (puede lanzar ServicioInvalidoError)
            self.__costo_total = self.__servicio.calcular_costo(
                duracion=self.__duracion,
                descuento=descuento,
                con_impuesto=con_impuesto
            )
            self.__estado = ESTADO_CONFIRMADA

        except OperacionNoPermitidaError as e:
            logger.error(f"Reserva {self.id_entidad} - {e}")
            raise

        except (ServicioNoDisponibleError, ClienteInvalidoError) as e:
            logger.error(f"Reserva {self.id_entidad} no confirmada: {e}")
            # Encadenamiento de excepciones: raise X from Y
            raise ReservaInvalidaError(
                f"No se pudo confirmar la reserva {self.id_entidad}: {e}"
            ) from e

        except Exception as e:
            logger.critical(f"Error inesperado al confirmar {self.id_entidad}: {e}")
            raise ReservaInvalidaError(
                f"Error inesperado al confirmar la reserva: {e}"
            ) from e

        else:
            # Solo se ejecuta si NO hubo ninguna excepción
            logger.info(
                f"Reserva {self.id_entidad} CONFIRMADA | "
                f"Costo: ${self.__costo_total:,.0f}"
            )
            print(f"  ✅ Reserva {self.id_entidad} confirmada. "
                  f"Costo total: ${self.__costo_total:,.0f}")

        finally:
            # Se ejecuta SIEMPRE, con o sin error
            logger.debug(
                f"Proceso de confirmación de {self.id_entidad} finalizado. "
                f"Estado actual: {self.__estado}"
            )

    def cancelar(self, motivo="Sin motivo especificado"):
        """
        Cancela la reserva si está en estado PENDIENTE o CONFIRMADA.
        Demuestra: try / except / finally
        """
        logger.info(f"Intentando cancelar reserva {self.id_entidad}...")
        try:
            if self.__estado == ESTADO_CANCELADA:
                raise OperacionNoPermitidaError(
                    "cancelar", "la reserva ya estaba cancelada"
                )
            self.__estado = ESTADO_CANCELADA
            self.__notas += f" | Cancelada: {motivo}"

        except OperacionNoPermitidaError as e:
            logger.warning(f"Cancelación inválida en {self.id_entidad}: {e}")
            raise

        finally:
            logger.debug(f"Proceso de cancelación de {self.id_entidad} terminado.")

        logger.info(f"Reserva {self.id_entidad} CANCELADA | Motivo: {motivo}")
        print(f"  🚫 Reserva {self.id_entidad} cancelada. Motivo: {motivo}")

    def __str__(self):
        return (f"Reserva({self.id_entidad}, "
                f"cliente={self.__cliente.id_entidad}, "
                f"servicio={self.__servicio.id_entidad}, "
                f"estado={self.__estado}, "
                f"costo=${self.__costo_total:,.0f})")


# =============================================================================
# 8. GESTOR DEL SISTEMA
# =============================================================================

class GestorSistema:
    """
    Coordina todas las operaciones del sistema Software FJ.
    Mantiene en memoria (sin base de datos) las listas de
    clientes, servicios y reservas.
    """
    def __init__(self):
        self.__clientes  = {}   # id → objeto Cliente
        self.__servicios = {}   # id → objeto Servicio
        self.__reservas  = {}   # id → objeto Reserva
        self.__total_operaciones    = 0
        self.__operaciones_exitosas = 0
        self.__operaciones_fallidas = 0
        logger.info("Sistema Software FJ iniciado correctamente.")
        print("=" * 55)
        print("   SISTEMA SOFTWARE FJ — GESTIÓN DE SERVICIOS")
        print("=" * 55)

    # ── Clientes ─────────────────────────────────────────────────────────────
    def registrar_cliente(self, id_cliente, nombre, email, telefono):
        """Registra un cliente con validación completa. Demuestra try/except/else/finally."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Registrando cliente: {nombre}...")
        try:
            if id_cliente in self.__clientes:
                raise ClienteDuplicadoError(id_cliente)
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
            self.__clientes[id_cliente] = cliente
            self.__operaciones_exitosas += 1
            logger.info(f"Cliente {id_cliente} registrado exitosamente.")
            print(f"  ✅ Cliente '{nombre}' registrado con ID: {id_cliente}")
            return cliente

        finally:
            logger.debug(f"Fin registro cliente {id_cliente}. "
                         f"Total clientes: {len(self.__clientes)}")

    # ── Servicios ────────────────────────────────────────────────────────────
    def registrar_sala(self, id_servicio, nombre_sala, tipo_sala, capacidad):
        """Registra una sala de reuniones."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Registrando sala: {nombre_sala}...")
        try:
            sala = ReservaSala(id_servicio, nombre_sala, tipo_sala, capacidad)
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

    # ── Reservas ─────────────────────────────────────────────────────────────
    def crear_reserva(self, id_reserva, id_cliente, id_servicio,
                      duracion, descuento=0, con_impuesto=False, notas=""):
        """Crea y confirma una reserva con manejo completo de excepciones."""
        self.__total_operaciones += 1
        print(f"\n[OP {self.__total_operaciones}] Creando reserva {id_reserva}...")
        try:
            if id_cliente not in self.__clientes:
                raise ReservaInvalidaError(f"No existe cliente con ID '{id_cliente}'.")
            if id_servicio not in self.__servicios:
                raise ReservaInvalidaError(f"No existe servicio con ID '{id_servicio}'.")

            cliente  = self.__clientes[id_cliente]
            servicio = self.__servicios[id_servicio]
            reserva  = Reserva(id_reserva, cliente, servicio, duracion, notas)
            reserva.confirmar(descuento=descuento, con_impuesto=con_impuesto)
            self.__reservas[id_reserva] = reserva
            self.__operaciones_exitosas += 1
            return reserva

        except (ReservaInvalidaError, OperacionNoPermitidaError, SistemaFJError) as e:
            self.__operaciones_fallidas += 1
            logger.error(f"Reserva {id_reserva} fallida: {e}")
            print(f"  ❌ Error en reserva: {e}")
            return None

        except Exception as e:
            self.__operaciones_fallidas += 1
            logger.critical(f"Error crítico en reserva {id_reserva}: {e}")
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
            print(f"  ⚠️  {e}")

    # ── Reportes ─────────────────────────────────────────────────────────────
    def listar_clientes(self):
        print("\n" + "─" * 55)
        print("  CLIENTES REGISTRADOS")
        print("─" * 55)
        if not self.__clientes:
            print("  (No hay clientes registrados)")
            return
        for c in self.__clientes.values():
            print(f"  • {c}")

    def listar_servicios(self):
        print("\n" + "─" * 55)
        print("  SERVICIOS REGISTRADOS")
        print("─" * 55)
        if not self.__servicios:
            print("  (No hay servicios registrados)")
            return
        for s in self.__servicios.values():
            s.mostrar_info()

    def listar_reservas(self):
        print("\n" + "─" * 55)
        print("  RESERVAS DEL SISTEMA")
        print("─" * 55)
        if not self.__reservas:
            print("  (No hay reservas registradas)")
            return
        for r in self.__reservas.values():
            r.mostrar_info()

    def mostrar_estadisticas(self):
        print("\n" + "=" * 55)
        print("  ESTADÍSTICAS DEL SISTEMA")
        print("=" * 55)
        confirmadas = sum(1 for r in self.__reservas.values() if r.estado == ESTADO_CONFIRMADA)
        canceladas  = sum(1 for r in self.__reservas.values() if r.estado == ESTADO_CANCELADA)
        print(f"  Total operaciones   : {self.__total_operaciones}")
        print(f"  Operaciones exitosas: {self.__operaciones_exitosas}")
        print(f"  Operaciones fallidas: {self.__operaciones_fallidas}")
        print(f"  Clientes registrados: {len(self.__clientes)}")
        print(f"  Servicios activos   : {len(self.__servicios)}")
        print(f"  Reservas totales    : {len(self.__reservas)}")
        print(f"  Reservas confirmadas: {confirmadas}")
        print(f"  Reservas canceladas : {canceladas}")
        print("=" * 55)
        logger.info("Estadísticas del sistema consultadas.")


# =============================================================================
# 9. FUNCIÓN PRINCIPAL — SIMULACIÓN DE 21 OPERACIONES
# =============================================================================

def separador(titulo):
    """Imprime un separador visual entre secciones."""
    print(f"\n{'─' * 55}")
    print(f"  {titulo}")
    print(f"{'─' * 55}")


def main():
    gestor = GestorSistema()

    # ── CLIENTES ──────────────────────────────────────────────────────────────
    separador("REGISTRO DE CLIENTES")

    gestor.registrar_cliente("CLI001", "Ana García López",  "ana.garcia@email.com",     "3201234567")   # ✅ válido
    gestor.registrar_cliente("CLI002", "Carlos Pérez",      "correo_sin_arroba",         "3109876543")   # ❌ email inválido
    gestor.registrar_cliente("CLI002", "Carlos Pérez Ruiz", "carlos.perez@email.com",   "3109876543")   # ✅ válido
    gestor.registrar_cliente("CLI001", "Otro Usuario",      "otro@email.com",            "3001112222")   # ❌ duplicado
    gestor.registrar_cliente("CLI003", "12345",             "invalido@email.com",        "3005556677")   # ❌ nombre inválido
    gestor.registrar_cliente("CLI003", "María Torres",      "maria.torres@empresa.co",  "6017654321")   # ✅ válido

    # ── SERVICIOS ─────────────────────────────────────────────────────────────
    separador("REGISTRO DE SERVICIOS")

    gestor.registrar_sala    ("SRV001", "Sala Innovación",      "mediana",        20)    # ✅ válido
    gestor.registrar_sala    ("SRV002", "Auditorio Principal",  "auditorio",     100)    # ✅ válido
    gestor.registrar_equipo  ("SRV003", "laptop",               10)                      # ✅ válido
    gestor.registrar_equipo  ("SRV004", "holografo",             2)                      # ❌ tipo inválido
    gestor.registrar_asesoria("SRV005", "python",               "Ing. Luis Fernández")   # ✅ válido
    gestor.registrar_asesoria("SRV006", "ciberseguridad",       "Ing. Sandra Morales")   # ✅ válido

    # ── RESERVAS ──────────────────────────────────────────────────────────────
    separador("CREACIÓN DE RESERVAS")

    gestor.crear_reserva("RES001", "CLI001", "SRV001", 3, notas="Reunión de planeación")          # ✅ sala 3 horas
    gestor.crear_reserva("RES002", "CLI002", "SRV003", 5, descuento=10, con_impuesto=True,
                         notas="Alquiler para capacitación")                                       # ✅ equipo con descuento+IVA
    gestor.crear_reserva("RES003", "CLI003", "SRV005", 4, notas="Capacitación en Python")         # ✅ asesoría
    gestor.crear_reserva("RES004", "CLI999", "SRV001", 2)                                          # ❌ cliente no existe

    # Desactivar un servicio para probar el error
    print("\n  [Acción] Desactivando Auditorio Principal...")
    gestor._GestorSistema__servicios["SRV002"].disponible = False
    print("  ⚠️  Auditorio Principal marcado como no disponible.")

    gestor.crear_reserva("RES005", "CLI001", "SRV002", 2)                                          # ❌ servicio no disponible
    gestor.crear_reserva("RES006", "CLI001", "SRV001", 99)                                         # ❌ duración inválida (>12h)

    # ── CANCELACIONES ─────────────────────────────────────────────────────────
    separador("CANCELACIÓN DE RESERVAS")

    gestor.cancelar_reserva("RES001", motivo="El cliente reprogramó la reunión")    # ✅ cancelación exitosa
    gestor.cancelar_reserva("RES001", motivo="Intento duplicado")                   # ❌ ya cancelada
    gestor.cancelar_reserva("RES999", motivo="Error de sistema")                    # ❌ no existe

    # ── REPORTES ──────────────────────────────────────────────────────────────
    separador("REPORTE FINAL DEL SISTEMA")

    gestor.listar_clientes()
    gestor.listar_reservas()
    gestor.mostrar_estadisticas()

    print("\n  📋 Logs guardados en: sistema_fj.log")
    print("  Sistema finalizado correctamente.\n")
    logger.info("Simulación completa. Sistema cerrado correctamente.")


# =============================================================================
# PUNTO DE ENTRADA
# Este bloque solo se ejecuta si corres este archivo directamente:
#   python software_fj_completo.py
# =============================================================================
if __name__ == "__main__":
    main()