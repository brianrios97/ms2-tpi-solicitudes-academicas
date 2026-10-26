"""
Pruebas unitarias de los enums de dominio (Refactoring #4).
No tocan disco.

Ejecutar con: python -m unittest test_dominio -v
"""

import unittest

from dominio import (
    EstadoSolicitud,
    Prioridad,
    TipoTramite,
)


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


if __name__ == "__main__":
    unittest.main()
