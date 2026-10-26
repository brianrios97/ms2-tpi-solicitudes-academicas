"""
Pruebas unitarias de registrar_solicitud.
Usan un JSON temporal para no modificar data/solicitudes.json.

Ejecutar con: python -m unittest test_registro_solicitud -v
"""
import contextlib
import io
import os
import tempfile
import unittest

from app import DatosRegistroSolicitud, SistemaGestionAcademica


def registrar(sistema, **campos):
    base = {
        "legajo": "EST-200",
        "nombre": "Ana Perez",
        "email": "ana@alumnos.edu.ar",
        "carrera": "Tecnicatura en Programacion",
        "tipo": "Pase de Carrera",
        "prioridad": "BAJA",
        "descripcion": "Solicitud de cambio de carrera por motivos laborales.",
        "observaciones": "",
    }
    base.update(campos)
    return sistema.registrar_solicitud(DatosRegistroSolicitud(**base))


class RegistrarSolicitudTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.tmp.name, "solicitudes.json")
        self.sistema = SistemaGestionAcademica(self.ruta)

    def tearDown(self):
        self.tmp.cleanup()

    def registrar(self, **campos):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            resultado = registrar(self.sistema, **campos)
        return resultado, salida.getvalue()

    def solicitudes(self):
        return self.sistema.datos["solicitudes"]

    def test_registro_valido_persiste_todos_los_campos(self):
        nuevo_id, salida = self.registrar(observaciones="Adjunta recibo")

        self.assertEqual(nuevo_id, 1)
        self.assertEqual(salida, "")
        sol = self.solicitudes()[0]
        self.assertEqual(sol["id"], 1)
        self.assertEqual(sol["estudiante_legajo"], "EST-200")
        self.assertEqual(sol["estudiante_nombre"], "Ana Perez")
        self.assertEqual(sol["estudiante_email"], "ana@alumnos.edu.ar")
        self.assertEqual(sol["estudiante_carrera"], "Tecnicatura en Programacion")
        self.assertEqual(sol["tipo"], "Pase de Carrera")
        self.assertEqual(sol["descripcion"], "Solicitud de cambio de carrera por motivos laborales.")
        self.assertEqual(sol["estado"], "PENDIENTE")
        self.assertIsNone(sol["responsable_id"])
        self.assertEqual(sol["observaciones"], "Adjunta recibo")
        self.assertRegex(sol["fecha_creacion"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_registro_valido_guarda_en_disco(self):
        self.registrar()
        reabierto = SistemaGestionAcademica(self.ruta)
        self.assertEqual(len(reabierto.datos["solicitudes"]), 1)

    def test_ids_son_correlativos(self):
        self.assertEqual(self.registrar()[0], 1)
        self.assertEqual(self.registrar()[0], 2)
        self.assertEqual(self.registrar()[0], 3)

    def test_estudiante_nuevo_se_agrega_una_sola_vez(self):
        self.registrar(legajo="EST-300")
        self.registrar(legajo="EST-300")
        legajos = [e["legajo"] for e in self.sistema.datos["estudiantes"]]
        self.assertEqual(legajos, ["EST-300"])
        self.assertEqual(
            self.sistema.datos["estudiantes"][0],
            {"legajo": "EST-300", "nombre": "Ana Perez",
             "email": "ana@alumnos.edu.ar", "carrera": "Tecnicatura en Programacion"},
        )

    def assertRechazado(self, resultado, salida, mensaje):
        self.assertEqual(resultado, -1)
        self.assertEqual(salida.strip(), mensaje)
        self.assertEqual(self.solicitudes(), [])
        self.assertEqual(self.sistema.datos["estudiantes"], [])

    def test_rechaza_datos_de_estudiante_vacios(self):
        for campo in ("legajo", "nombre", "email"):
            with self.subTest(campo=campo):
                resultado, salida = self.registrar(**{campo: ""})
                self.assertRechazado(resultado, salida, "Error: Los datos del estudiante son obligatorios.")

    def test_rechaza_email_sin_arroba(self):
        resultado, salida = self.registrar(email="ana.alumnos.edu.ar")
        self.assertRechazado(resultado, salida, "Error: El correo electronico del estudiante no es valido.")

    def test_rechaza_email_sin_punto(self):
        resultado, salida = self.registrar(email="ana@alumnos")
        self.assertRechazado(resultado, salida, "Error: El correo electronico del estudiante no es valido.")

    def test_rechaza_descripcion_corta_o_vacia(self):
        for descripcion in ("", "corta", "   corta   "):
            with self.subTest(descripcion=descripcion):
                resultado, salida = self.registrar(descripcion=descripcion)
                self.assertRechazado(
                    resultado, salida,
                    "Error: La descripcion debe tener al menos 10 caracteres explicativos.")

    def test_acepta_descripcion_de_exactamente_10_caracteres(self):
        resultado, _ = self.registrar(descripcion="1234567890")
        self.assertEqual(resultado, 1)

    def test_valida_primero_los_datos_del_estudiante(self):
        resultado, salida = self.registrar(legajo="", email="malo", descripcion="x")
        self.assertRechazado(resultado, salida, "Error: Los datos del estudiante son obligatorios.")

    def prioridad_resultante(self, tipo, prioridad):
        resultado, salida = self.registrar(tipo=tipo, prioridad=prioridad)
        self.assertGreater(resultado, 0)
        return self.solicitudes()[-1]["prioridad"], salida

    def test_certificado_fuerza_prioridad_media(self):
        self.assertEqual(self.prioridad_resultante("Certificado de Alumno Regular", "ALTA")[0], "MEDIA")

    def test_reclamo_de_examen_fuerza_prioridad_alta(self):
        self.assertEqual(self.prioridad_resultante("Reclamo de Examen", "BAJA")[0], "ALTA")

    def test_pase_de_carrera_fuerza_prioridad_baja(self):
        self.assertEqual(self.prioridad_resultante("Pase de Carrera", "ALTA")[0], "BAJA")

    def test_equivalencia_respeta_prioridad_valida_normalizada(self):
        self.assertEqual(self.prioridad_resultante("Equivalencia de Materia", " baja ")[0], "BAJA")
        self.assertEqual(self.prioridad_resultante("Equivalencia de Materia", "media")[0], "MEDIA")

    def test_equivalencia_con_prioridad_invalida_o_vacia(self):
        self.assertEqual(self.prioridad_resultante("Equivalencia de Materia", "URGENTE")[0], "ALTA")
        self.assertEqual(self.prioridad_resultante("Equivalencia de Materia", "")[0], "MEDIA")

    def test_tipo_desconocido_advierte_y_conserva_prioridad(self):
        prioridad, salida = self.prioridad_resultante("Beca", "alta")
        self.assertEqual(prioridad, "ALTA")
        self.assertEqual(salida.strip(), "Advertencia: Tipo de tramite desconocido 'Beca'.")

    def test_prioridad_vacia_por_defecto_es_media(self):
        self.assertEqual(self.prioridad_resultante("Beca", "")[0], "MEDIA")


if __name__ == "__main__":
    unittest.main()
