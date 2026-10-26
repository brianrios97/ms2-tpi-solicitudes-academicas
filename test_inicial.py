"""
Script de verificacion automatizada del estado inicial del sistema.
Ejecuta las operaciones principales y demuestra que el sistema funciona
externamente (Calidad Externa OK) antes de aplicar cualquier refactor.
"""
from app import SistemaGestionAcademica, DatosRegistroSolicitud

def main():
    print("=== VERIFICACION DE ESTADO INICIAL ===")
    sistema = SistemaGestionAcademica("data/solicitudes.json")

    # 1. Verificar carga de datos
    print(f"Estudiantes cargados: {len(sistema.datos['estudiantes'])}")
    print(f"Responsables cargados: {len(sistema.datos['responsables'])}")
    print(f"Solicitudes cargadas: {len(sistema.datos['solicitudes'])}")

    # 2. Registrar nueva solicitud
    print("\n--- TEST: Registrar Solicitud ---")
    nuevo_id = sistema.registrar_solicitud(DatosRegistroSolicitud(
        legajo="EST-104",
        nombre="Sofia Martinez",
        email="sofia.m@alumnos.edu.ar",
        carrera="Tecnicatura Universitaria en Programacion",
        tipo="Pase de Carrera",
        prioridad="BAJA",
        descripcion="Solicitud de cambio de comision por razones laborales.",
        observaciones="Adjunta recibo de sueldo"
    ))
    print(f"Solicitud creada con ID: {nuevo_id}")
    assert nuevo_id > 0, "Fallo al registrar solicitud"

    # 3. Asignar responsable
    print("\n--- TEST: Asignar Responsable ---")
    ok_asig = sistema.asignar_responsable(nuevo_id, "RESP-01")
    print(f"Asignacion exitosa: {ok_asig}")
    sol = sistema.obtener_solicitud_por_id(nuevo_id)
    assert sol["responsable_id"] == "RESP-01", "Fallo asignacion de responsable"
    assert sol["estado"] == "EN_CURSO", "Fallo transicion de estado a EN_CURSO"

    # 4. Cambiar estado
    print("\n--- TEST: Cambiar Estado a RESUELTA ---")
    ok_est = sistema.cambiar_estado(nuevo_id, "RESUELTA", "Aprobado pase de turno noche")
    print(f"Cambio de estado exitoso: {ok_est}")
    sol = sistema.obtener_solicitud_por_id(nuevo_id)
    assert sol["estado"] == "RESUELTA", "Fallo transicion a RESUELTA"

    # 5. Filtrar solicitudes
    print("\n--- TEST: Buscar y Filtrar ---")
    filtradas = sistema.buscar_solicitudes(filtro_estado="RESUELTA")
    print(f"Solicitudes con estado RESUELTA: {len(filtradas)}")
    assert len(filtradas) >= 2, "Fallo filtro de solicitudes"

    # 6. Reporte general
    print("\n--- TEST: Generar Reporte de Metricas ---")
    rep = sistema.generar_reporte_general()
    print("Reporte generado:")
    for k, v in rep.items():
        print(f"  {k}: {v}")

    print("\n>>> TODAS LAS PRUEBAS DE CALIDAD EXTERNA PASARON CON EXITO <<<")

if __name__ == "__main__":
    main()
