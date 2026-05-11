# =============================================================================
# ARCHIVO: servicios.py
# DESCRIPCIÓN: Define la clase abstracta Servicio y los tres servicios
#              especializados de Software FJ.
#
# Jerarquía:
#   EntidadBase  (abstracta)
#     └── Servicio (abstracta)
#           ├── ReservaSala
#           ├── AlquilerEquipo
#           └── Asesoria
#
# Conceptos demostrados:
#   - Herencia en dos niveles
#   - Polimorfismo: calcular_costo() distinto en cada clase
#   - Métodos sobrecargados (con parámetros opcionales)
#   - Encapsulación con @property
# =============================================================================

from abc import abstractmethod          # Para declarar métodos abstractos
from entidades import EntidadBase       # Clase raíz del sistema
from excepciones import ServicioInvalidoError, ServicioNoDisponibleError
from logger import logger


# =============================================================================
# CLASE ABSTRACTA SERVICIO
# Segundo nivel de la jerarquía. Define el contrato para todos los servicios.
# =============================================================================
class Servicio(EntidadBase):
    """
    Clase abstracta que representa un servicio de Software FJ.
    Hereda de EntidadBase y agrega métodos específicos de servicios.
    """

    def __init__(self, id_servicio, nombre, descripcion, disponible=True):
        """
        Parámetros:
            id_servicio : str  → identificador único del servicio
            nombre      : str  → nombre comercial del servicio
            descripcion : str  → descripción breve
            disponible  : bool → si el servicio está activo u ofertado
        """
        # Llamamos al constructor de EntidadBase
        super().__init__(id_servicio)
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__disponible = disponible

    # ── Getters ────────────────────────────────────────────────────────
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
        """Permite cambiar la disponibilidad del servicio."""
        self.__disponible = bool(valor)

    # ── Métodos abstractos: cada servicio los implementa a su manera ───
    @abstractmethod
    def calcular_costo(self, duracion, descuento=0, con_impuesto=False):
        """
        Calcula el costo del servicio.
        El parámetro 'duracion' significa algo diferente en cada servicio:
          - ReservaSala   → horas
          - AlquilerEquipo → días
          - Asesoria      → número de sesiones
        """
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida que la duración y otros parámetros sean correctos."""
        pass

    # ── Método concreto compartido por todos ──────────────────────────
    def verificar_disponibilidad(self):
        """
        Verifica si el servicio está disponible.
        Si no lo está, lanza ServicioNoDisponibleError.
        """
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)
        return True

    # Implementación de métodos abstractos de EntidadBase
    def validar(self):
        return self.__disponible

    def mostrar_info(self):
        estado = "✅ Disponible" if self.__disponible else "❌ No disponible"
        print(f"  Servicio [{self.id_entidad}]: {self.__nombre} — {estado}")


# =============================================================================
# SERVICIO 1: RESERVA DE SALA
# Costo = precio por hora × cantidad de horas × capacidad (factor de escala)
# =============================================================================
class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones o conferencias.
    La duración se mide en HORAS.
    """

    # Precio base por hora según capacidad de la sala
    PRECIOS_POR_CAPACIDAD = {
        "pequeña":  25000,   # Hasta 10 personas
        "mediana":  45000,   # Hasta 25 personas
        "grande":   80000,   # Hasta 50 personas
        "auditorio":150000,  # Más de 50 personas
    }

    def __init__(self, id_servicio, nombre_sala, tipo_sala, capacidad_maxima):
        """
        Parámetros:
            id_servicio     : str → identificador único
            nombre_sala     : str → nombre de la sala (ej: "Sala Innovación")
            tipo_sala       : str → "pequeña", "mediana", "grande", "auditorio"
            capacidad_maxima: int → número máximo de personas
        """
        # Guardamos los atributos propios antes de llamar al padre
        self.__nombre_sala = nombre_sala
        self.__tipo_sala = tipo_sala.lower()
        self.__capacidad_maxima = capacidad_maxima

        # Obtenemos el precio base según el tipo de sala
        precio_hora = self.PRECIOS_POR_CAPACIDAD.get(self.__tipo_sala, 0)
        self.__precio_hora = precio_hora

        # Llamamos al constructor del padre (Servicio)
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
        """
        Valida que la duración (en horas) sea válida.
        También verifica que el tipo de sala exista.
        """
        # Verificamos el tipo de sala
        if self.__tipo_sala not in self.PRECIOS_POR_CAPACIDAD:
            raise ServicioInvalidoError(
                f"Tipo de sala '{self.__tipo_sala}' no existe. "
                f"Opciones: {list(self.PRECIOS_POR_CAPACIDAD.keys())}"
            )
        # Verificamos la duración
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ServicioInvalidoError(
                "La duración (horas) debe ser un número positivo."
            )
        # Se limita la reserva máxima de salas a 12 horas continuas
        if duracion > 12:
            raise ServicioInvalidoError(
                "No se puede reservar una sala por más de 12 horas seguidas."
            )
        return True

    def calcular_costo(self, duracion, descuento=0, con_impuesto=False):
        """
        Calcula el costo de la reserva de sala.

        Fórmula: precio_hora × horas
        Con descuento   : calcular_costo(4, descuento=15)
        Con IVA (19%)   : calcular_costo(4, con_impuesto=True)

        Parámetros:
            duracion    : int/float → número de horas
            descuento   : float → porcentaje de descuento (0-100)
            con_impuesto: bool  → si se aplica IVA del 19%
        """
        # Validamos antes de calcular
        self.validar_parametros(duracion)

        # Costo base
        costo = self.__precio_hora * duracion

        # Aplicamos descuento si corresponde
        if descuento > 0:
            if not (0 < descuento < 100):
                raise ServicioInvalidoError("El descuento debe estar entre 0 y 100.")
            costo = costo * (1 - descuento / 100)

        # Aplicamos impuesto si corresponde
        if con_impuesto:
            costo = costo * 1.19   # IVA del 19%

        return round(costo, 2)

    def mostrar_info(self):
        """Muestra la información completa de la sala."""
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


# =============================================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# Costo = precio_por_dia × cantidad × días
# =============================================================================
class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    La duración se mide en DÍAS.
    """

    # Precio base por día según tipo de equipo
    PRECIOS_POR_EQUIPO = {
        "laptop":     80000,
        "proyector":  50000,
        "impresora":  30000,
        "servidor":  150000,
        "tablet":     40000,
    }

    def __init__(self, id_servicio, tipo_equipo, cantidad_disponible):
        """
        Parámetros:
            id_servicio        : str → identificador único
            tipo_equipo        : str → tipo de equipo (ver PRECIOS_POR_EQUIPO)
            cantidad_disponible: int → unidades disponibles para alquilar
        """
        self.__tipo_equipo = tipo_equipo.lower()
        self.__cantidad_disponible = cantidad_disponible
        self.__precio_dia = self.PRECIOS_POR_EQUIPO.get(self.__tipo_equipo, 0)

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
        """
        Valida el tipo de equipo, la cantidad solicitada y los días.

        Parámetros extra:
            cantidad: int → unidades que se quieren alquilar
        """
        if self.__tipo_equipo not in self.PRECIOS_POR_EQUIPO:
            raise ServicioInvalidoError(
                f"Equipo '{self.__tipo_equipo}' no existe. "
                f"Opciones: {list(self.PRECIOS_POR_EQUIPO.keys())}"
            )
        if not isinstance(duracion, int) or duracion <= 0:
            raise ServicioInvalidoError(
                "La duración (días) debe ser un número entero positivo."
            )
        if duracion > 30:
            raise ServicioInvalidoError(
                "No se puede alquilar un equipo por más de 30 días."
            )
# Verifica que existan suficientes equipos disponibles para el alquiler
        if cantidad > self.__cantidad_disponible:
            raise ServicioInvalidoError(
                f"Solo hay {self.__cantidad_disponible} unidades disponibles "
                f"de {self.__tipo_equipo}. Se solicitaron {cantidad}."
            )
        return True

    def calcular_costo(self, duracion, descuento=0, con_impuesto=False, cantidad=1):
        """
        Calcula el costo del alquiler de equipo.

        Fórmula: precio_dia × días × cantidad
        Ejemplos:
            calcular_costo(5)                          → básico
            calcular_costo(5, cantidad=3)              → 3 laptops 5 días
            calcular_costo(5, descuento=10, cantidad=2)→ con descuento
        """
        self.validar_parametros(duracion, cantidad)

        costo = self.__precio_dia * duracion * cantidad
# Verifica si el usuario desea aplicar un descuento al servicio
        if descuento > 0:
            if not (0 < descuento < 100):
                raise ServicioInvalidoError("El descuento debe estar entre 0 y 100.")
            costo = costo * (1 - descuento / 100)
# Aplica el IVA correspondiente al costo total del servicio
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


# =============================================================================
# SERVICIO 3: ASESORÍA ESPECIALIZADA
# Costo = tarifa_por_sesion × número de sesiones
# =============================================================================
class Asesoria(Servicio):
    """
    Servicio de asesoría especializada por un consultor.
    La duración se mide en número de SESIONES.
    """

    # Tarifa por sesión según especialidad
    TARIFAS_POR_ESPECIALIDAD = {
        "python":           120000,
        "java":             120000,
        "bases_de_datos":   100000,
        "redes":            110000,
        "ciberseguridad":   150000,
        "inteligencia_artificial": 200000,
        "gestion_proyectos": 90000,
    }

    def __init__(self, id_servicio, especialidad, nombre_consultor):
        """
        Parámetros:
            id_servicio     : str → identificador único
            especialidad    : str → área de conocimiento (ver TARIFAS)
            nombre_consultor: str → nombre del experto asignado
        """
        self.__especialidad = especialidad.lower()
        self.__nombre_consultor = nombre_consultor
        self.__tarifa_sesion = self.TARIFAS_POR_ESPECIALIDAD.get(
            self.__especialidad, 0
        )

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
        """
        Valida la especialidad y el número de sesiones.
        'duracion' aquí representa el número de sesiones.
        """
        if self.__especialidad not in self.TARIFAS_POR_ESPECIALIDAD:
            raise ServicioInvalidoError(
                f"Especialidad '{self.__especialidad}' no disponible. "
                f"Opciones: {list(self.TARIFAS_POR_ESPECIALIDAD.keys())}"
            )
        if not isinstance(duracion, int) or duracion <= 0:
            raise ServicioInvalidoError(
                "El número de sesiones debe ser un entero positivo."
            )
     # Se controla que las asesorías no excedan el número permitido de sesiones
        if duracion > 20:
            raise ServicioInvalidoError(
                "No se pueden contratar más de 20 sesiones a la vez."
            )
        return True

    def calcular_costo(self, duracion, descuento=0, con_impuesto=False):
        """
        Calcula el costo total de la asesoría.

        Fórmula: tarifa_sesion × número_sesiones
        Ejemplos:
            calcular_costo(3)                    → 3 sesiones básico
            calcular_costo(5, descuento=20)      → con descuento VIP
            calcular_costo(3, con_impuesto=True) → con IVA
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
