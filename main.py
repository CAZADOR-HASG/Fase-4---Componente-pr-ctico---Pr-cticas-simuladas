# =============================================================================
# ARCHIVO: main.py
# DESCRIPCIÓN: Punto de entrada del sistema. Simula más de 10 operaciones
#              completas incluyendo casos válidos e inválidos.
#
# Operaciones simuladas:
#  1.  Registro de cliente válido           → exitoso
#  2.  Registro de cliente con email malo   → falla controlada
#  3.  Registro de cliente duplicado        → falla controlada
#  4.  Registro de sala válida              → exitoso
#  5.  Registro de equipo válido            → exitoso
#  6.  Registro de asesoría válida          → exitoso
#  7.  Registro de equipo con tipo inválido → falla controlada
#  8.  Reserva de sala válida               → exitosa
#  9.  Reserva con descuento e IVA          → exitosa
# 10.  Reserva de equipo                   → exitosa
# 11.  Reserva con cliente inexistente      → falla controlada
# 12.  Reserva con servicio no disponible   → falla controlada
# 13.  Cancelación válida de reserva        → exitosa
# 14.  Cancelación de reserva ya cancelada  → falla controlada
# 15.  Listado completo y estadísticas      → reporte final
# =============================================================================

from gestor import GestorSistema
from logger import logger


def separador(titulo):
    """Imprime un separador visual entre secciones."""
    print(f"\n{'─' * 55}")
    print(f"  {titulo}")
    print(f"{'─' * 55}")


def main():
    """Función principal que ejecuta la simulación del sistema."""

    # Creamos el gestor del sistema (inicializa las listas internas)
    gestor = GestorSistema()

    # =========================================================================
    # SECCIÓN 1: REGISTRO DE CLIENTES
    # =========================================================================
    separador("REGISTRO DE CLIENTES")

    # OP 1: Cliente válido → debe registrarse sin problemas
    gestor.registrar_cliente(
        id_cliente="CLI001",
        nombre="Ana García López",
        email="ana.garcia@email.com",
        telefono="3201234567"
    )

    # OP 2: Cliente con email inválido → debe fallar con ClienteInvalidoError
    gestor.registrar_cliente(
        id_cliente="CLI002",
        nombre="Carlos Pérez",
        email="correo_sin_arroba",      # ← email inválido
        telefono="3109876543"
    )

    # OP 3: Segundo cliente válido
    gestor.registrar_cliente(
        id_cliente="CLI002",
        nombre="Carlos Pérez Ruiz",
        email="carlos.perez@email.com",
        telefono="3109876543"
    )

    # OP 4: Cliente duplicado → debe fallar con ClienteDuplicadoError
    gestor.registrar_cliente(
        id_cliente="CLI001",           # ← ID ya existe
        nombre="Otro Usuario",
        email="otro@email.com",
        telefono="3001112222"
    )

    # OP 5: Cliente con nombre inválido → debe fallar
    gestor.registrar_cliente(
        id_cliente="CLI003",
        nombre="12345",                # ← solo números, inválido
        email="invalido@email.com",
        telefono="3005556677"
    )

    # OP 6: Tercer cliente válido
    gestor.registrar_cliente(
        id_cliente="CLI003",
        nombre="María Torres",
        email="maria.torres@empresa.co",
        telefono="6017654321"
    )

    # =========================================================================
    # SECCIÓN 2: REGISTRO DE SERVICIOS
    # =========================================================================
    separador("REGISTRO DE SERVICIOS")

    # OP 7: Sala mediana válida
    gestor.registrar_sala(
        id_servicio="SRV001",
        nombre_sala="Sala Innovación",
        tipo_sala="mediana",
        capacidad=20
    )

    # OP 8: Sala grande válida
    gestor.registrar_sala(
        id_servicio="SRV002",
        nombre_sala="Auditorio Principal",
        tipo_sala="auditorio",
        capacidad=100
    )

    # OP 9: Equipo válido (laptops)
    gestor.registrar_equipo(
        id_servicio="SRV003",
        tipo_equipo="laptop",
        cantidad=10
    )

    # OP 10: Equipo con tipo inválido → debe fallar
    gestor.registrar_equipo(
        id_servicio="SRV004",
        tipo_equipo="holografo",       # ← no existe en el catálogo
        cantidad=2
    )

    # OP 11: Asesoría válida en Python
    gestor.registrar_asesoria(
        id_servicio="SRV005",
        especialidad="python",
        consultor="Ing. Luis Fernández"
    )

    # OP 12: Asesoría en ciberseguridad
    gestor.registrar_asesoria(
        id_servicio="SRV006",
        especialidad="ciberseguridad",
        consultor="Ing. Sandra Morales"
    )

    # =========================================================================
    # SECCIÓN 3: CREACIÓN DE RESERVAS
    # =========================================================================
    separador("CREACIÓN DE RESERVAS")

    # OP 13: Reserva válida de sala → debe confirmarse
    gestor.crear_reserva(
        id_reserva="RES001",
        id_cliente="CLI001",
        id_servicio="SRV001",
        duracion=3,                    # 3 horas
        notas="Reunión de planeación estratégica"
    )

    # OP 14: Reserva con descuento e IVA → debe confirmarse
    gestor.crear_reserva(
        id_reserva="RES002",
        id_cliente="CLI002",
        id_servicio="SRV003",
        duracion=5,                    # 5 días
        descuento=10,                  # 10% de descuento
        con_impuesto=True,             # Con IVA del 19%
        notas="Alquiler para capacitación"
    )

    # OP 15: Reserva de asesoría válida
    gestor.crear_reserva(
        id_reserva="RES003",
        id_cliente="CLI003",
        id_servicio="SRV005",
        duracion=4,                    # 4 sesiones
        notas="Capacitación en Python para el equipo"
    )

    # OP 16: Reserva con cliente inexistente → debe fallar
    gestor.crear_reserva(
        id_reserva="RES004",
        id_cliente="CLI999",           # ← no existe
        id_servicio="SRV001",
        duracion=2
    )

    # OP 17: Marcamos un servicio como no disponible y luego intentamos reservarlo
    print("\n  [Acción manual] Desactivando servicio SRV002...")
    # Accedemos al servicio directamente para desactivarlo
    servicio_auditorio = gestor._GestorSistema__servicios.get("SRV002")
    if servicio_auditorio:
        servicio_auditorio.disponible = False
        print("  ⚠️  Auditorio Principal marcado como no disponible.")

    # OP 18: Reserva con servicio no disponible → debe fallar
    gestor.crear_reserva(
        id_reserva="RES005",
        id_cliente="CLI001",
        id_servicio="SRV002",          # ← no disponible
        duracion=2
    )

    # OP 19: Reserva con duración inválida → debe fallar
    gestor.crear_reserva(
        id_reserva="RES006",
        id_cliente="CLI001",
        id_servicio="SRV001",
        duracion=99,                   # ← más de 12 horas (límite de salas)
    )

    # =========================================================================
    # SECCIÓN 4: CANCELACIÓN DE RESERVAS
    # =========================================================================
    separador("CANCELACIÓN DE RESERVAS")

    # OP 20: Cancelar reserva existente → debe cancelarse
    gestor.cancelar_reserva(
        id_reserva="RES001",
        motivo="El cliente reprogramó la reunión"
    )

    # OP 21: Cancelar reserva ya cancelada → debe fallar
    gestor.cancelar_reserva(
        id_reserva="RES001",           # ← ya fue cancelada arriba
        motivo="Intento duplicado"
    )

    # OP 22: Cancelar reserva inexistente → debe fallar
    gestor.cancelar_reserva(
        id_reserva="RES999",           # ← no existe
        motivo="Error de sistema"
    )

    # =========================================================================
    # SECCIÓN 5: REPORTES FINALES
    # =========================================================================
    separador("REPORTE FINAL DEL SISTEMA")

    gestor.listar_clientes()
    gestor.listar_reservas()
    gestor.mostrar_estadisticas()

    print("\n  📋 Los logs completos están en: sistema_fj.log")
    print("  Sistema finalizado correctamente.\n")
    logger.info("Simulación completa. Sistema cerrado correctamente.")


# Punto de entrada del programa
# Este bloque solo se ejecuta si corremos este archivo directamente
if __name__ == "__main__":
    main()
