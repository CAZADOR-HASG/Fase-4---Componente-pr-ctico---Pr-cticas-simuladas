# =============================================================================
# ARCHIVO: entidades.py
# DESCRIPCIÓN: Define la clase abstracta base del sistema y la clase Cliente.
#
# Contenido:
#   - EntidadBase : clase abstracta raíz de todas las entidades
#   - Cliente     : gestiona datos personales con encapsulación y validaciones
# =============================================================================

from abc import ABC, abstractmethod   # Para crear clases abstractas
import re                             # Para validar email con expresiones regulares
from datetime import datetime         # Para registrar fecha de creación
from excepciones import ClienteInvalidoError   # Nuestras excepciones personalizadas
from logger import logger                       # Nuestro sistema de logs


# =============================================================================
# CLASE ABSTRACTA BASE
# Es la raíz de toda la jerarquía de clases del sistema.
# Obliga a que todas las entidades tengan un ID y un método para mostrarse.
# =============================================================================
class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad del sistema Software FJ.
    Todas las clases principales (Cliente, Servicio, Reserva) heredan de aquí.
    """

    def __init__(self, id_entidad):
        # El ID es privado: solo se accede mediante el getter
        self.__id_entidad = id_entidad
        # Guardamos la fecha y hora exacta en que se creó esta entidad
        self.__fecha_creacion = datetime.now()

    # ── Getters ────────────────────────────────────────────────────────
    @property
    def id_entidad(self):
        """Retorna el ID de la entidad (solo lectura)."""
        return self.__id_entidad

    @property
    def fecha_creacion(self):
        """Retorna la fecha de creación (solo lectura)."""
        return self.__fecha_creacion

    # ── Métodos abstractos que TODOS los hijos deben implementar ───────
    @abstractmethod
    def mostrar_info(self):
        """Muestra la información completa de la entidad."""
        pass

    @abstractmethod
    def validar(self):
        """Valida que los datos de la entidad sean correctos."""
        pass

    # ── Método concreto (compartido por todos los hijos) ───────────────
    def obtener_fecha_str(self):
        """Retorna la fecha de creación como texto legible."""
        return self.__fecha_creacion.strftime("%d/%m/%Y %H:%M:%S")


# =============================================================================
# CLASE CLIENTE
# Gestiona la información personal de los clientes de Software FJ.
# Implementa encapsulación: todos los atributos son privados (__)
# Solo se acceden mediante @property (getters) y setters con validación.
# =============================================================================
class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.
    Hereda de EntidadBase e implementa sus métodos abstractos.
    """

    def __init__(self, id_cliente, nombre, email, telefono):
        """
        Crea un cliente con validaciones estrictas.

        Parámetros:
            id_cliente : str → identificador único (ej: "CLI001")
            nombre     : str → nombre completo
            email      : str → correo electrónico válido
            telefono   : str → teléfono de 7 a 10 dígitos
        """
        # Primero llamamos al constructor del padre (EntidadBase)
        super().__init__(id_cliente)

        # Usamos los setters para asignar con validación automática
        # Si algún dato es inválido, el setter lanzará ClienteInvalidoError
        self.nombre = nombre        # → llama a @nombre.setter
        self.email = email          # → llama a @email.setter
        self.telefono = telefono    # → llama a @telefono.setter

        # Estado del cliente: activo por defecto
        self.__activo = True

        # Registramos la creación exitosa en el log
        logger.info(f"Cliente creado: {id_cliente} - {nombre}")

    # ── GETTERS: permiten leer los atributos privados ──────────────────

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

    # ── SETTERS: permiten modificar con validación ─────────────────────

    @nombre.setter
    def nombre(self, valor):
        """
        Valida y asigna el nombre.
        Reglas: no puede estar vacío, mínimo 3 caracteres, solo letras y espacios.
        """
        # strip() elimina espacios al inicio y al final
        if not valor or not valor.strip():
            raise ClienteInvalidoError(
                "El nombre no puede estar vacío.", campo="nombre"
            )
        if len(valor.strip()) < 3:
            raise ClienteInvalidoError(
                "El nombre debe tener al menos 3 caracteres.", campo="nombre"
            )
        # Verificamos que solo tenga letras, espacios y tildes
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", valor.strip()):
            raise ClienteInvalidoError(
                "El nombre solo puede contener letras y espacios.", campo="nombre"
            )
        # title() capitaliza la primera letra de cada palabra
        self.__nombre = valor.strip().title()

    @email.setter
    def email(self, valor):
        """
        Valida y asigna el email.
        Regla: debe tener formato válido (algo@algo.algo)
        """
        if not valor or not valor.strip():
            raise ClienteInvalidoError(
                "El email no puede estar vacío.", campo="email"
            )
        # Expresión regular para validar formato de email
        patron_email = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, valor.strip()):
            raise ClienteInvalidoError(
                f"El email '{valor}' no tiene un formato válido.", campo="email"
            )
        self.__email = valor.strip().lower()

    @telefono.setter
    def telefono(self, valor):
        """
        Valida y asigna el teléfono.
        Regla: debe contener entre 7 y 10 dígitos numéricos.
        """
        if not valor or not valor.strip():
            raise ClienteInvalidoError(
                "El teléfono no puede estar vacío.", campo="telefono"
            )
        # Eliminamos espacios, guiones y paréntesis para quedarnos solo con dígitos
        solo_digitos = re.sub(r"[\s\-\(\)]", "", valor.strip())
        if not solo_digitos.isdigit():
            raise ClienteInvalidoError(
                "El teléfono solo puede contener números.", campo="telefono"
            )
        if not (7 <= len(solo_digitos) <= 10):
            raise ClienteInvalidoError(
                "El teléfono debe tener entre 7 y 10 dígitos.", campo="telefono"
            )
        self.__telefono = solo_digitos

    # ── Métodos abstractos implementados ──────────────────────────────

    def validar(self):
        """
        Verifica que el cliente esté en estado válido para operar.
        Retorna True si puede hacer reservas, False si está inactivo.
        """
        if not self.__activo:
            logger.warning(f"Cliente {self.id_entidad} inactivo intentó operar.")
            return False
        return True

    def mostrar_info(self):
        """Imprime la ficha completa del cliente."""
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

    # ── Métodos adicionales ────────────────────────────────────────────

    def desactivar(self):
        """Desactiva el cliente, impidiendo que haga nuevas reservas."""
        self.__activo = False
        logger.info(f"Cliente {self.id_entidad} desactivado.")

    def __str__(self):
        """Representación corta del cliente."""
        return f"Cliente({self.id_entidad}, {self.__nombre}, {self.__email})"

    def __repr__(self):
        """Representación técnica del cliente."""
        return (f"Cliente(id='{self.id_entidad}', nombre='{self.__nombre}', "
                f"email='{self.__email}', tel='{self.__telefono}')")
