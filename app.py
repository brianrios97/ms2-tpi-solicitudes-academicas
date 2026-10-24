"""
================================================================================
SISTEMA DE GESTION DE SOLICITUDES ACADEMICAS (VERSION BASE / ESTADO-INICIAL)
Asignatura: Metodologia de Sistemas II - Trabajo Practico Integrador
Integrantes: Rios Brian, Rivero Albornoz Juan Pablo, Riveros Valganon Nahuel

NOTA DE DISENO (ESTADO INICIAL):
Este archivo representa el estado inicial del sistema con fines academicos.
Funciona correctamente desde el punto de vista del usuario (calidad externa),
pero contiene deliberadamente deuda tecnica y code smells para su posterior
diagnostico y refactorizacion profesional (calidad interna).
================================================================================
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DatosRegistroSolicitud:
    """Parameter Object: agrupa los datos necesarios para registrar una solicitud."""
    legajo: str
    nombre: str
    email: str
    carrera: str
    tipo: str
    prioridad: str
    descripcion: str
    observaciones: str = ""


class SistemaGestionAcademica:
    """
    SMELL 1: GOD CLASS / LARGE CLASS
    Esta clase concentra responsabilidades de:
    - Manejo de persistencia y E/S de archivos JSON.
    - Logica de negocio y validaciones de dominio.
    - Generacion y calculo de reportes y metricas.
    - Interfaz de usuario por consola (inputs, prints, formateos).
    """

    def __init__(self, ruta_archivo="data/solicitudes.json"):
        # SMELL 6: MAGIC STRING (ruta de archivo por defecto y cadenas hardcodeadas)
        self.ruta_archivo = ruta_archivo
        self.datos = {"estudiantes": [], "responsables": [], "solicitudes": []}
        self.cargar_datos()

    # SMELL 7: DUPLICATE CODE (Lectura y manejo de archivo replicado en metodos)
    def cargar_datos(self):
        try:
            if os.path.exists(self.ruta_archivo):
                with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                    self.datos = json.load(f)
            else:
                self.guardar_datos()
        # SMELL 8: EXCEPTION SWALLOWING / POBRE MANEJO DE ERRORES
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            self.datos = {"estudiantes": [], "responsables": [], "solicitudes": []}

    def guardar_datos(self):
        try:
            directorio = os.path.dirname(self.ruta_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return False

    def registrar_solicitud(self, datos):
        """Devuelve el ID asignado, o -1 si los datos no son validos."""
        if not self._datos_son_validos(datos):
            return -1

        prioridad_final = self._calcular_prioridad(datos.tipo, datos.prioridad)

        self._registrar_estudiante_si_no_existe(datos)

        nuevo_id = self._generar_nuevo_id()
        self.datos["solicitudes"].append(
            self._construir_solicitud(nuevo_id, datos, prioridad_final)
        )
        self.guardar_datos()
        return nuevo_id

    def _datos_son_validos(self, datos):
        return (
            self._validar_datos_estudiante(datos)
            and self._validar_email(datos.email)
            and self._validar_descripcion(datos.descripcion)
        )

    def _validar_datos_estudiante(self, datos):
        if not datos.legajo or not datos.nombre or not datos.email:
            print("Error: Los datos del estudiante son obligatorios.")
            return False
        return True

    def _validar_email(self, email):
        if "@" not in email or "." not in email:
            print("Error: El correo electronico del estudiante no es valido.")
            return False
        return True

    def _validar_descripcion(self, descripcion):
        if not descripcion or len(descripcion.strip()) < 10:
            print("Error: La descripcion debe tener al menos 10 caracteres explicativos.")
            return False
        return True

    # SMELL 5: CONDITIONAL CHAINS / SWITCH STATEMENTS
    # Logica condicional para validar o forzar prioridad segun tipo de tramite
    def _calcular_prioridad(self, tipo, prioridad):
        prioridad_final = prioridad.upper().strip() if prioridad else "MEDIA"
        if tipo == "Equivalencia de Materia":
            if prioridad_final != "ALTA" and prioridad_final != "MEDIA" and prioridad_final != "BAJA":
                prioridad_final = "ALTA"
        elif tipo == "Certificado de Alumno Regular":
            prioridad_final = "MEDIA"
        elif tipo == "Reclamo de Examen":
            prioridad_final = "ALTA"
        elif tipo == "Pase de Carrera":
            prioridad_final = "BAJA"
        else:
            print(f"Advertencia: Tipo de tramite desconocido '{tipo}'.")
        return prioridad_final

    def _registrar_estudiante_si_no_existe(self, datos):
        existe = any(est["legajo"] == datos.legajo for est in self.datos["estudiantes"])
        if not existe:
            self.datos["estudiantes"].append({
                "legajo": datos.legajo,
                "nombre": datos.nombre,
                "email": datos.email,
                "carrera": datos.carrera
            })

    def _generar_nuevo_id(self):
        if not self.datos["solicitudes"]:
            return 1
        return max(s["id"] for s in self.datos["solicitudes"]) + 1

    def _construir_solicitud(self, nuevo_id, datos, prioridad_final):
        return {
            "id": nuevo_id,
            "estudiante_legajo": datos.legajo,
            "estudiante_nombre": datos.nombre,
            "estudiante_email": datos.email,
            "estudiante_carrera": datos.carrera,
            "tipo": datos.tipo,
            "descripcion": datos.descripcion,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prioridad": prioridad_final,
            # SMELL 6: MAGIC STRING
            "estado": "PENDIENTE",
            "responsable_id": None,
            "observaciones": datos.observaciones
        }

    # OPERACION 2: ASIGNAR RESPONSABLE
    def asignar_responsable(self, id_solicitud, id_responsable):
        solicitud = self.obtener_solicitud_por_id(id_solicitud)
        if not solicitud:
            print(f"Error: No existe solicitud con ID {id_solicitud}.")
            return False

        responsable = self.obtener_responsable_por_id(id_responsable)
        if not responsable:
            print(f"Error: No existe responsable con ID {id_responsable}.")
            return False

        solicitud["responsable_id"] = id_responsable
        # Si estaba pendiente, al asignar pasa a 'EN_CURSO'
        if solicitud["estado"] == "PENDIENTE":
            solicitud["estado"] = "EN_CURSO"

        self.guardar_datos()
        return True

    # OPERACION 3: CAMBIAR ESTADO
    def cambiar_estado(self, id_solicitud, nuevo_estado, obs=""):
        solicitud = self.obtener_solicitud_por_id(id_solicitud)
        if not solicitud:
            print(f"Error: Solicitud {id_solicitud} no encontrada.")
            return False

        # SMELL 6: MAGIC STRINGS
        estados_validos = ["PENDIENTE", "EN_CURSO", "RESUELTA", "RECHAZADA"]
        nuevo_estado_upper = nuevo_estado.upper().strip()

        if nuevo_estado_upper not in estados_validos:
            print(f"Error: Estado invalido '{nuevo_estado}'. Debe ser uno de {estados_validos}")
            return False

        # Validaciones de transicion
        if solicitud["estado"] == "RESUELTA" or solicitud["estado"] == "RECHAZADA":
            print(f"Error: La solicitud {id_solicitud} ya esta finalizada ({solicitud['estado']}).")
            return False

        if nuevo_estado_upper == "RESUELTA" and not solicitud["responsable_id"]:
            print("Error: No se puede resolver una solicitud sin un responsable asignado.")
            return False

        solicitud["estado"] = nuevo_estado_upper
        if obs:
            solicitud["observaciones"] = (solicitud.get("observaciones", "") + " | " + obs).strip(" | ")

        self.guardar_datos()
        return True

    # OPERACION 4: BUSCAR Y FILTRAR
    def buscar_solicitudes(self, filtro_estado=None, filtro_legajo=None, filtro_responsable=None):
        resultados = []
        for sol in self.datos["solicitudes"]:
            coincide = True
            if filtro_estado and sol["estado"].upper() != filtro_estado.upper():
                coincide = False
            if filtro_legajo and sol["estudiante_legajo"].upper() != filtro_legajo.upper():
                coincide = False
            if filtro_responsable and sol["responsable_id"] != filtro_responsable:
                coincide = False

            if coincide:
                resultados.append(sol)
        return resultados

    # OPERACION 5: REPORTE GENERAL DE GESTION
    def generar_reporte_general(self):
        """Calcula metricas agregadas y muestra resumen estadistico."""
        total = len(self.datos["solicitudes"])
        pendientes = sum(1 for s in self.datos["solicitudes"] if s["estado"] == "PENDIENTE")
        en_curso = sum(1 for s in self.datos["solicitudes"] if s["estado"] == "EN_CURSO")
        resueltas = sum(1 for s in self.datos["solicitudes"] if s["estado"] == "RESUELTA")
        rechazadas = sum(1 for s in self.datos["solicitudes"] if s["estado"] == "RECHAZADA")

        reporte = {
            "total_solicitudes": total,
            "pendientes": pendientes,
            "en_curso": en_curso,
            "resueltas": resueltas,
            "rechazadas": rechazadas,
            "tasa_resolucion": round((resueltas / total * 100), 2) if total > 0 else 0.0
        }
        return reporte

    # AUXILIARES
    def obtener_solicitud_por_id(self, id_solicitud):
        for sol in self.datos["solicitudes"]:
            if sol["id"] == int(id_solicitud):
                return sol
        return None

    def obtener_responsable_por_id(self, id_responsable):
        for resp in self.datos["responsables"]:
            if resp["id"] == id_responsable:
                return resp
        return None

    def listar_responsables(self):
        return self.datos["responsables"]


# ==============================================================================
# INTERFAZ DE USUARIO POR CONSOLA (MENU CLI)
# ==============================================================================
def mostrar_menu():
    print("\n" + "=" * 60)
    print("  SISTEMA DE GESTION DE SOLICITUDES ACADEMICAS - TPI MS2")
    print("=" * 60)
    print("1. Registrar nueva solicitud")
    print("2. Listar todas las solicitudes")
    print("3. Asignar responsable a una solicitud")
    print("4. Cambiar estado de una solicitud")
    print("5. Filtrar solicitudes (por estado / estudiante)")
    print("6. Ver reporte de gestion y metricas")
    print("7. Listar responsables academicos")
    print("0. Salir")
    print("=" * 60)

def ejecutar_cli():
    sistema = SistemaGestionAcademica()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion [0-7]: ").strip()

        if opcion == "1":
            print("\n--- REGISTRAR NUEVA SOLICITUD ---")
            legajo = input("Legajo estudiante (ej. EST-104): ").strip()
            nombre = input("Nombre completo: ").strip()
            email = input("Email: ").strip()
            carrera = input("Carrera: ").strip()
            print("Tipos sugeridos: Equivalencia de Materia, Certificado de Alumno Regular, Reclamo de Examen, Pase de Carrera")
            tipo = input("Tipo de tramite: ").strip()
            prioridad = input("Prioridad (ALTA, MEDIA, BAJA): ").strip()
            descripcion = input("Descripcion del motivo (min 10 caracteres): ").strip()
            obs = input("Observaciones adicionales (opcional): ").strip()

            datos = DatosRegistroSolicitud(
                legajo=legajo, nombre=nombre, email=email, carrera=carrera,
                tipo=tipo, prioridad=prioridad, descripcion=descripcion, observaciones=obs
            )
            nuevo_id = sistema.registrar_solicitud(datos)
            if nuevo_id > 0:
                print(f"\n>> Solicitud #{nuevo_id} registrada con exito en estado PENDIENTE.")
            else:
                print("\n>> No se pudo registrar la solicitud debido a errores de validacion.")

        elif opcion == "2":
            print("\n--- LISTADO GENERAL DE SOLICITUDES ---")
            solicitudes = sistema.datos["solicitudes"]
            if not solicitudes:
                print("No hay solicitudes registradas.")
            else:
                for s in solicitudes:
                    print(f"[{s['id']}] {s['fecha_creacion']} | {s['tipo']} | Est: {s['estudiante_nombre']} ({s['estudiante_legajo']})")
                    print(f"     Estado: {s['estado']} | Prioridad: {s['prioridad']} | Resp: {s['responsable_id'] or 'Sin asignar'}")
                    print(f"     Desc: {s['descripcion']}")
                    if s.get("observaciones"):
                        print(f"     Obs: {s['observaciones']}")
                    print("-" * 55)

        elif opcion == "3":
            print("\n--- ASIGNAR RESPONSABLE ---")
            try:
                id_sol = int(input("Ingrese ID de la solicitud: "))
                print("Responsables disponibles:")
                for r in sistema.listar_responsables():
                    print(f"  - {r['id']}: {r['nombre']} ({r['area']})")
                id_resp = input("ID de Responsable a asignar (ej. RESP-01): ").strip()
                if sistema.asignar_responsable(id_sol, id_resp):
                    print(f">> Solicitud #{id_sol} asignada con exito a {id_resp}.")
            except ValueError:
                print("Error: El ID debe ser un numero entero.")

        elif opcion == "4":
            print("\n--- CAMBIAR ESTADO ---")
            try:
                id_sol = int(input("Ingrese ID de la solicitud: "))
                nuevo_estado = input("Nuevo estado (PENDIENTE, EN_CURSO, RESUELTA, RECHAZADA): ").strip()
                obs = input("Motivo o resolucion: ").strip()
                if sistema.cambiar_estado(id_sol, nuevo_estado, obs):
                    print(f">> Estado de solicitud #{id_sol} actualizado a {nuevo_estado.upper()}.")
            except ValueError:
                print("Error: El ID debe ser un numero entero.")

        elif opcion == "5":
            print("\n--- FILTRAR SOLICITUDES ---")
            filtro_est = input("Filtrar por estado (Enter para omitir): ").strip() or None
            filtro_leg = input("Filtrar por legajo estudiante (Enter para omitir): ").strip() or None
            resultados = sistema.buscar_solicitudes(filtro_estado=filtro_est, filtro_legajo=filtro_leg)
            print(f"\nResultados encontrados: {len(resultados)}")
            for s in resultados:
                print(f"[{s['id']}] {s['tipo']} | {s['estado']} | {s['estudiante_nombre']} | Resp: {s['responsable_id'] or 'N/A'}")

        elif opcion == "6":
            print("\n--- REPORTE DE GESTION Y METRICAS ---")
            reporte = sistema.generar_reporte_general()
            print(f"Total de Solicitudes: {reporte['total_solicitudes']}")
            print(f"  - Pendientes : {reporte['pendientes']}")
            print(f"  - En Curso   : {reporte['en_curso']}")
            print(f"  - Resueltas  : {reporte['resueltas']}")
            print(f"  - Rechazadas : {reporte['rechazadas']}")
            print(f"Tasa de Resolucion: {reporte['tasa_resolucion']}%")

        elif opcion == "7":
            print("\n--- RESPONSABLES ACADEMICOS REGISTRADOS ---")
            for r in sistema.listar_responsables():
                print(f"[{r['id']}] {r['nombre']} - Area: {r['area']}")

        elif opcion == "0":
            print("\nSaliendo del sistema. Cambios guardados.")
            break
        else:
            print("Opcion invalida. Intente nuevamente.")

if __name__ == "__main__":
    ejecutar_cli()
