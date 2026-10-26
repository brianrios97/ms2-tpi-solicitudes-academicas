"""
Pruebas unitarias de los enums de dominio (Refactoring #4).
No tocan disco.

Ejecutar con: python -m unittest test_dominio -v
"""

import unittest

from dominio import (
    EstadoSolicitud,
    Prioridad,
    Solicitud,
    TipoTramite,
    TransicionInvalidaError,
)


def nueva_solicitud(**cambios):
    datos = {
        "id": 7,
        "estudiante_legajo": "EST-200",
        "estudiante_nombre": "Ana Perez",
        "estudiante_email": "ana@alumnos.edu.ar",
        "estudiante_carrera": "Tecnicatura en Programacion",
        "tipo": "Reclamo de Examen",
        "descripcion": "Reclamo por nota del parcial.",
        "fecha_creacion": "2026-10-20 10:00:00",
        "prioridad": "ALTA",
        "estado": "PENDIENTE",
        "responsable_id": None,
        "observaciones": "",
    }
    datos.update(cambios)
    return Solicitud.desde_dict(datos)


class EnumsTest(unittest.TestCase):
    def test_estado_desde_texto_normaliza_mayusculas_y_espacios(self):
        self.assertIs(
            EstadoSolicitud.desde_texto(" resuelta "), EstadoSolicitud.RESUELTA
        )

    def test_estado_desde_texto_invalido_devuelve_none(self):
        for texto in ("CERRADA", "", None):
            with self.subTest(texto=texto):
                self.assertIsNone(EstadoSolicitud.desde_texto(texto))

    def test_estados_finales(self):
        self.assertTrue(EstadoSolicitud.RESUELTA.es_final)
        self.assertTrue(EstadoSolicitud.RECHAZADA.es_final)
        self.assertFalse(EstadoSolicitud.PENDIENTE.es_final)
        self.assertFalse(EstadoSolicitud.EN_CURSO.es_final)

    def test_valores_conservan_el_orden_original(self):
        self.assertEqual(
            EstadoSolicitud.valores(),
            ["PENDIENTE", "EN_CURSO", "RESUELTA", "RECHAZADA"],
        )
        self.assertEqual(Prioridad.valores(), ["ALTA", "MEDIA", "BAJA"])

    def test_tipo_desde_texto_es_exacto(self):
        self.assertIs(
            TipoTramite.desde_texto("Pase de Carrera"), TipoTramite.PASE_CARRERA
        )
        self.assertIsNone(TipoTramite.desde_texto("pase de carrera"))
        self.assertIsNone(TipoTramite.desde_texto("Beca"))


class ResolverPrioridadTest(unittest.TestCase):
    def test_tipos_con_prioridad_fija_ignoran_la_solicitada(self):
        casos = {
            TipoTramite.CERTIFICADO_REGULAR: Prioridad.MEDIA,
            TipoTramite.RECLAMO_EXAMEN: Prioridad.ALTA,
            TipoTramite.PASE_CARRERA: Prioridad.BAJA,
        }
        for tipo, esperada in casos.items():
            for solicitada in (Prioridad.ALTA, Prioridad.BAJA, None):
                with self.subTest(tipo=tipo, solicitada=solicitada):
                    self.assertIs(tipo.resolver_prioridad(solicitada), esperada)

    def test_equivalencia_respeta_la_solicitada(self):
        self.assertIs(
            TipoTramite.EQUIVALENCIA.resolver_prioridad(Prioridad.BAJA), Prioridad.BAJA
        )

    def test_equivalencia_sin_prioridad_valida_usa_alta(self):
        self.assertIs(TipoTramite.EQUIVALENCIA.resolver_prioridad(None), Prioridad.ALTA)


class SolicitudTest(unittest.TestCase):
    def test_ida_y_vuelta_dict_conserva_formato_persistido(self):
        original = nueva_solicitud(observaciones="algo").a_dict()
        self.assertEqual(Solicitud.desde_dict(original).a_dict(), original)
        self.assertEqual(original["estado"], "PENDIENTE")
        self.assertIsInstance(original["estado"], str)

    def test_asignar_responsable_pasa_pendiente_a_en_curso(self):
        sol = nueva_solicitud()
        sol.asignar_responsable("RESP-01")
        self.assertEqual(sol.responsable_id, "RESP-01")
        self.assertIs(sol.estado, EstadoSolicitud.EN_CURSO)

    def test_asignar_responsable_no_cambia_otros_estados(self):
        sol = nueva_solicitud(estado="RESUELTA", responsable_id="RESP-01")
        sol.asignar_responsable("RESP-02")
        self.assertEqual(sol.responsable_id, "RESP-02")
        self.assertIs(sol.estado, EstadoSolicitud.RESUELTA)

    def test_no_se_puede_resolver_sin_responsable(self):
        sol = nueva_solicitud()
        with self.assertRaisesRegex(TransicionInvalidaError, "sin un responsable"):
            sol.cambiar_estado(EstadoSolicitud.RESUELTA)
        self.assertIs(sol.estado, EstadoSolicitud.PENDIENTE)

    def test_se_puede_rechazar_sin_responsable(self):
        sol = nueva_solicitud()
        sol.cambiar_estado(EstadoSolicitud.RECHAZADA, "Fuera de termino")
        self.assertIs(sol.estado, EstadoSolicitud.RECHAZADA)
        self.assertEqual(sol.observaciones, "Fuera de termino")

    def test_solicitud_finalizada_no_admite_cambios(self):
        for final in ("RESUELTA", "RECHAZADA"):
            with self.subTest(final=final):
                sol = nueva_solicitud(estado=final, responsable_id="RESP-01")
                with self.assertRaisesRegex(
                    TransicionInvalidaError, f"ya esta finalizada \\({final}\\)"
                ):
                    sol.cambiar_estado(EstadoSolicitud.EN_CURSO)

    def test_observaciones_se_concatenan_con_separador(self):
        sol = nueva_solicitud(observaciones="Primera", responsable_id="RESP-01")
        sol.cambiar_estado(EstadoSolicitud.RESUELTA, "Aprobada")
        self.assertEqual(sol.observaciones, "Primera | Aprobada")

    def test_observacion_vacia_no_modifica(self):
        sol = nueva_solicitud(observaciones="Primera")
        sol.cambiar_estado(EstadoSolicitud.EN_CURSO, "")
        self.assertEqual(sol.observaciones, "Primera")


if __name__ == "__main__":
    unittest.main()
